#   Copyright 2013 Daniel Stokes, Mitchell Stokes
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import math
from bge import logic, constraints, types
from mathutils import Vector
from .animations import AnimationManager, AnimationState
from . import utils


class Character(types.KX_GameObject):
	"""	A character wrapper"""

	MAX_HP = 10  #: Maximum HP for the character

	MAX_SPEED = 0.10  #: Maximum speed of the character
	MAX_AIR_SPEED = MAX_SPEED * 0.75  #: Maximum speed while airborne
	ACCELERATION = 0.01  #: How much to accelerate the character while moving
	DECELERATION = ACCELERATION * 10  #: How much to deccelerate the character while not moving
	FRICTION = ACCELERATION  #: Amount of friction applied to the character while moving and stopping

	RUN_MULTIPLIER = 2.0  #: How many times faster the character (and their move animations) are while running

	GRAVITY = 9.8 * 5  #: Starting gravity value for the Bullet character controller

	MESH = "Sinbad"  #: The name of the blendfile and object to use for spawning an instance of the character

	#: Mapping of animation names to their actions. Each item is a dictionary of keyword arguments to KX_GameObject.playAction(), and each item is played in its own layer.
	#:
	#: The following animation names are currently recognized by the default Character class:
	#:
	#:     idle
	#:         Idle Animation (the character isn't moving or airborne)
	#:     move
	#:         The character is moving on the ground (i.e., not airborne)
	#:     jump
	#:         The character is airborne
	#:     dead
	#:         The character is dead
	ANIMATIONS = {}

	class IdleAnimState(AnimationState):
		def update(self):
			return self.character.ANIMATIONS.get('idle')

	class MoveAnimState(AnimationState):
		def update(self):
			anim = self.character.ANIMATIONS.get('move')
			if anim:
				for i in anim:
					i['speed'] = self.character.RUN_MULTIPLIER if self.character.running else 1.0
			return anim

	class JumpAnimState(AnimationState):
		def update(self):
			return self.character.ANIMATIONS.get('jump')

	class DeadAnimState(AnimationState):
		def update(self):
			return self.character.ANIMATIONS.get('dead')

	def __init__(self, obj):
		"""
		:param obj: The KX_GameObject to mutate

		.. warning::
		   You should never use this class's constructor, always use the :func:`spawn` method to create a character.
		"""
		types.KX_GameObject.__init__(obj)

		self._speed_h = Vector.Fill(2)
		self._flags = set()

		self._library = ""

		self.hp = self.MAX_HP

		l = [i for i in self.childrenRecursive if isinstance(i, types.BL_ArmatureObject)]
		if l:
			self._armature = l[0]
		else:
			self._armature = None

		# Don't play animations if this is true
		self.animation_lock = False

		# Enable double jump
		self._phy_char = constraints.getCharacter(self)
		self._phy_char.maxJumps = 2

		self.gravity = self.GRAVITY

		self.running = False

		self.animation_manager = AnimationManager(self, self.IdleAnimState)

	@property
	def is_dead(self):
		"""True if the character is dead"""
		return "DEAD" in self._flags

	@property
	def gravity(self):
		"""The current gravity value used for Bullet's character controller"""
		return self._phy_char.gravity

	@gravity.setter
	def gravity(self, value):
		self._phy_char.gravity = value

	@property
	def airborne(self):
		"""True if the character is in the air"""
		return not self._phy_char.onGround

	@property
	def armature(self):
		"""The object to use for playing animations"""
		return self._armature if self._armature else self

	@classmethod
	def spawn(cls, position=None, orientation=None):
		"""Spawns an instance of the character

		:param position: The world position of the new instance
		:param orientation: The world orientation of the new instance
		:rtype: The new character instance
		"""

		name = cls.MESH

		library = utils.get_path('characters', name+'.blend')
		logic.LibLoad(library, "Scene", load_actions=True)

		scene = logic.getCurrentScene()
		adder = logic.getCurrentController().owner
		if position:
			adder.worldPosition = position
		if orientation:
			adder.worldOrientation = orientation

		obj = scene.addObject(name, adder)

		char = cls(obj)
		char._library = library
		return char

	def free(self):
		"""Frees the blendfile used for the character"""
		if self._library:
			logic.LibFree(self._library)

	def rotate(self, rotation):
		"""Rotate the character about its z axis

		:param rotation: Amount of rotation in radians
		"""
		if not "DEAD" in self._flags:
			self.applyRotation(Vector((0, 0, rotation)))

	def update(self):
		"""Update method which should be called every frame to update this character"""
		if self.hp <= 0:
			self._flags.add("DEAD")
			self._apply_movement(Vector((0, 0, 0)))
			self.animation_manager.change_state(self.DeadAnimState)

		if self.is_dead:
			return

		if not self.airborne and self._speed_h.length_squared < 0.0001:
			self.animation_manager.change_state(self.IdleAnimState)

		self.animation_manager.update()

	def move(self, direction):
		"""Moves the player horizontally

		:param direction: A direction vector for the movement
		"""

		if self.is_dead:
			return

		# Determine the direction the player is moving
		momentum = self._speed_h.copy()
		momentum.normalize()

		if direction.length_squared != 0:

			# Normalize direction
			direction.normalize()

			# Accelerate player if not going fast enough
			if momentum.length_squared == 0 or momentum.angle(direction) < math.pi:
				self._speed_h += self.ACCELERATION * direction
			else:
				self._speed_h += self.DECELERATION * direction

			if not self.airborne:
				max_speed = self.MAX_SPEED * (self.RUN_MULTIPLIER if self.running else 1.0)
			else:
				max_speed = self.MAX_AIR_SPEED

			# print(player['speed_h'])
			if self._speed_h.length_squared > max_speed ** 2:
				self._speed_h = max_speed * direction
		else:  # Friction
			friction = min(self._speed_h.length, self.FRICTION) * momentum
			self._speed_h = self._speed_h - friction

		movement = self._speed_h.to_3d()
		self._apply_movement(movement)

		if movement.length_squared > 0.0001:
			# Face the player in the direction they are moving
			x = movement.cross(Vector((0, 0, 1)))
			x.normalize()

			y = movement.normalized()

			z = x.cross(y)
			z.normalize()

			ori = (
					(x[0], y[0], z[0]),
					(x[1], y[1], z[1]),
					(x[2], y[2], z[2])
				)

			self.localOrientation = ori

			# Handle animations
			if not self.airborne:
				self.animation_manager.change_state(self.MoveAnimState)

	def jump(self):
		"""Makes the character jump"""
		if self.is_dead:
			return

		self.animation_manager.change_state(self.JumpAnimState)

		self._phy_char.jump()

	def _apply_movement(self, vec):
		"""Applies a movement vector to the in game player object"""

		# Scale the speed so FPS changes don't mess with movement
		fps = logic.getAverageFrameRate()
		fps_scale = 60 / fps if fps != 0 else 60

		self._phy_char.walkDirection = vec * fps_scale
