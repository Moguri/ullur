import math
import time

from bge import logic, constraints, types
from mathutils import Vector, Matrix


class Character():
	MAX_HP = 10

	MAX_SPEED = 0.10
	MAX_AIR_SPEED = MAX_SPEED * 0.75
	ACCELERATION = 0.01
	DECELERATION = ACCELERATION * 10
	FRICTION = ACCELERATION

	GRAVITY = 9.8 * 5

	MESH = "Sinbad"

	ANIMATIONS = {
				"move": [('RunBase', 1, 20), ('RunTop', 1, 20)],
				"idle": [('IdleBase', 1, 220), ('IdleTop', 1, 300)],
				"jump_start": [('JumpStart', 1, 5)],
				"jump_loop": [('JumpLoop', 1, 30)],
				}

	def __init__(self, obj):
		self._speed_h = Vector.Fill(2)
		self._flags = set()

		self._library = ""

		self.hp = self.MAX_HP

		self._gameobj = obj

		l = [i for i in obj.childrenRecursive if isinstance(i, types.BL_ArmatureObject)]
		if l:
			self._armature = l[0]
		else:
			self._armature = None

		# Enable double jump
		self._phy_char = constraints.getCharacter(self._gameobj)
		self._phy_char.maxJumps = 2

		self.gravity = self.GRAVITY

	@property
	def is_dead(self):
		return "DEAD" in self._flags

	@property
	def gravity(self):
		return self._phy_char.gravity

	@gravity.setter
	def gravity(self, value):
		self._phy_char.gravity = value

	@property
	def airborne(self):
		return not self._phy_char.onGround

	@classmethod
	def spawn(cls, position=None, orientation=None):
		name = cls.MESH

		library = "//../characters/" + name + ".blend"
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
		if self._library:
			logic.LibFree(self._library)

	def rotate(self, rotation):
		if not "DEAD" in self._flags:
			self._gameobj.applyRotation(Vector((0, 0, rotation)))

	def animate(self, animation):
		if animation not in self.ANIMATIONS:
			print("WARNING: %s does not have animation %s" % (self.__class__.__name__, animation))
			return

		for layer, v in enumerate(self.ANIMATIONS[animation]):
			anim, start, end = v
			ob = self._armature if self._armature else self._gameobj

			ob.playAction(anim, start, end, play_mode=logic.KX_ACTION_MODE_LOOP, layer=layer, blendin=3, layer_weight=0.5)

	def stop_animation(self, layer):
		if self._armature:
			self._armature.stopAction(layer)
		else:
			self._gameobj.stopAction(layer)

	def update(self):
		if self.is_dead:
			return

		if self.hp <= 0:
			self._flags.add("DEAD")
			return

		if self.airborne:
			self.animate('jump_loop')
			self.stop_animation(1)
		elif self._speed_h.length_squared < 0.0001:
			self.animate('idle')
		else:
			self.animate('move')

	def move(self, direction):
		'''Moves the player horizontally'''

		if self.is_dead:
			return

		# Determine the direction the player is moving
		momentum = self._speed_h.copy()
		momentum.normalize()

		if self.is_attacking():
			# Only set direction, not movement
			if direction.length_squared > 0.0001:
				v = direction
				self.set_orientation_vector(Vector((v.x, v.y, 0)))
			direction = Vector((0, 0))

		if direction.length_squared != 0:

			# Normalize direction
			direction.normalize()

			# Accelerate player if not going fast enough
			if momentum.length_squared == 0 or momentum.angle(direction) < math.pi:
				self._speed_h += self.ACCELERATION * direction
			else:
				self._speed_h += self.DECELERATION * direction

			if not self.airborne:
				max_speed = self.MAX_SPEED
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

		# Face the player in the direction they are moving
		if movement.length_squared > 0.0001:
			self.set_orientation_vector(movement)

	def jump(self, double=False):
		if self.is_dead():
			return

		if not self.airborne and self._phy_char.jumpCount == 0:
			self.animate('jump_start')

		self._phy_char.jump()

	def _apply_movement(self, vec):
		'''Applies a movement vector to the in game player object'''

		# Scale the speed so FPS changes don't mess with movement
		fps = logic.getAverageFrameRate()
		fps_scale = 60 / fps if fps != 0 else 60

		self._phy_char.walkDirection = vec * fps_scale
