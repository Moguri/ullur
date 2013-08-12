import math

from bge import logic, constraints, types
from mathutils import Vector, Matrix


from .attack_manager import AttackSensor, MeleeAttackManager, MouseRangeAttackManager


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

	#: Mapping of animation names to their actions. The action is a list of:
	#:     ('name', start_frame, end_frame)
	#:
	#: Each item in this list is played in its own layer
	ANIMATIONS = {
				"move": [('RunBase', 1, 20), ('RunTop', 1, 20)],
				"idle": [('IdleBase', 1, 220), ('IdleTop', 1, 300)],
				"jump_start": [('JumpStart', 1, 5)],
				"jump_loop": [('JumpLoop', 1, 30)],
				"dead": [('Dance', 1, 71)],
				}

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

		self = self

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
		"""Frees the blendfile used for the character"""
		if self._library:
			logic.LibFree(self._library)

	def rotate(self, rotation):
		"""Rotate the character about its z axis

		:param rotation: Amount of rotation in radians
		"""
		if not "DEAD" in self._flags:
			self.applyRotation(Vector((0, 0, rotation)))

	def animate(self, animation, speed=1.0):
		"""Animate a character using its :attr:`ANIMATIONS` dictionary

		:param animation: The key for the animation to play
		:param speed: The playback speed for the animation
		"""
		if self.animation_lock:
			return

		if animation not in self.ANIMATIONS:
			print("WARNING: %s does not have animation %s" % (self.__class__.__name__, animation))
			return

		for layer, v in enumerate(self.ANIMATIONS[animation]):
			anim, start, end = v
			if anim == "*":
				continue
			ob = self.armature

			ob.playAction(anim, start, end, play_mode=logic.KX_ACTION_MODE_LOOP, layer=layer, blendin=3, layer_weight=0.5, speed=speed)

	def stop_animation(self, layer):
		"""Stop playing animations on a given layer

		:param layer: The layer to stop playing animations on
		"""
		if self._armature:
			self._armature.stopAction(layer)
		else:
			self.stopAction(layer)

	def update(self):
		"""Update method which should be called every frame to update this character"""
		if self.is_dead:
			self._apply_movement(Vector((0, 0, 0)))
			self.animate('dead')
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
			self.animate('move', self.RUN_MULTIPLIER if self.running else 1.0)

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

		# Face the player in the direction they are moving
		if movement.length_squared > 0.0001:
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

	def jump(self):
		"""Makes the character jump"""
		if self.is_dead:
			return

		if not self.airborne and self._phy_char.jumpCount == 0:
			self.animate('jump_start')

		self._phy_char.jump()

	def _apply_movement(self, vec):
		"""Applies a movement vector to the in game player object"""

		# Scale the speed so FPS changes don't mess with movement
		fps = logic.getAverageFrameRate()
		fps_scale = 60 / fps if fps != 0 else 60

		self._phy_char.walkDirection = vec * fps_scale


class Meatsack(Character):
	"""A character subclass for the Meatsack enemies"""
	MESH = "Cosbad"  #: See :attr:`Character.MESH`

	MELEE_ATTACK = [
			('SliceVertical', 1, 16),
		]

	def __init__(self, gameobj):
		super().__init__(gameobj)

		attack_sensors = [AttackSensor(i, self) for i in self.childrenRecursive if i.name.startswith('AttackSensor')]
		self.attack_manager = MeleeAttackManager(self, attack_sensors, self.MELEE_ATTACK, 5)

	def update(self):
		"""See :func:`Character.update`"""
		self.attack_manager.update()
		super().update()

	def attack(self):
		"""Makes the character perform a melee attack"""
		self.attack_manager.attack()



class UllurCharacter(Character):
	"""A character subclass for the player controlled character"""
	LEFT_MELEE_ATTACKS = [
			('Attack1', 1, 4),
			('Attack2', 1, 4),
		]

	RIGHT_MELEE_ATTACKS = [
			('SliceHorizontal', 1, 16),
		]

	def __init__(self, gameobj):
		super().__init__(gameobj)
		attack_sensors = [AttackSensor(i, self) for i in self.childrenRecursive if i.name.startswith('AttackSensor')]
		self.left_attack_manager = MeleeAttackManager(self, attack_sensors, self.LEFT_MELEE_ATTACKS, 5)
		#self.right_attack_manager = MeleeAttackManager(self, attack_sensors, self.RIGHT_MELEE_ATTACKS)
		self.right_attack_manager = MouseRangeAttackManager(self, "Projectile", 1, 100, 10, 0.5)
		self.collectables = []

	def update(self):
		"""See :func:`Character.update`"""
		self.left_attack_manager.update()
		self.right_attack_manager.update()
		super().update()

	def attack(self, mode):
		"""Makes the character attack

		:param mode: The attack manager to use, either 'LEFT' or 'RIGHT'
		"""

		if mode == "LEFT":
			self.stop_animation(1)
			self.left_attack_manager.attack()
		else:
			self.right_attack_manager.attack()

	def add_collectable(self, collectable):
		"""Adds a :class:`.Collectable` to the character

		:param collectable: The :class:`.Collectable` to add
		"""
		if collectable not in self.collectables:
			self.collectables.append(collectable)
