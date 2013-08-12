import time


from bge import types, logic
from mathutils import Vector

class AttackSensor(types.KX_GameObject):
	"""Sensor object that detects collisions for  :class:`.MeleeAttackManager`"""

	def __init__(self, gameobj, character):
		"""
		:param gameobj: The KX_GameObject to mutate (passed on to __new__)
		:param character: The :class:`scripts.character.Character` this sensor is attached too

		"""
		self._character = character
		self.collisionCallbacks.append(self._collision)

		if not hasattr(character, "_attack_hits"):
			character._attack_hits = set()

		self.detect_collisions = False
		self._damage = 0

	@property
	def _collisions(self):
		return self._character._attack_hits

	def __new__(cls, gameobj, *args):
		return super().__new__(cls, gameobj)

	def __del__(self):
		self.collisionCallbacks.remove(self.collision)

	def start_attack(self, damage):
		"""Notifies the sensor to begin dealing hits

		:param damage: How much damage hits cause
		"""

		self._damage = damage
		self.detect_collisions = True
		self._collisions.clear()

	def end_attack(self):
		"""Notifies the sensor to stop dealing hits"""

		self.detect_collisions = False

	def _collision(self, other):
		if not self.detect_collisions:
			return

		if other != self._character and hasattr(other, "hp") and other not in self._collisions:
			self._collisions.add(other)
			other.hp -= self._damage


class MeleeAttackManager:
	"""Handles melee attacks for :class:`.Character` objects"""

	def __init__(self, character, attack_sensors, attacks, damage):
		"""
		:param character: The :class:`.Character` this manager is attached to
		:param attack_sensors: A list of :class:`.AttackSensor` objects to be used for this manager
		:param attacks: A list of attacks ('name', start_frame, end_frame) to use
		:param damage: How much damage each hit should cause

		"""

		character._attack_time = time.time()
		self._attack_sensors = attack_sensors
		self._obj = character
		self._attacking = False
		self.combo = 0
		self.damage = damage

		self.attacks = attacks
		self.max_combo = len(attacks)

	@property
	def _attack_time(self):
		return self._obj._attack_time

	@_attack_time.setter
	def _attack_time(self, value):
		self._obj._attack_time = value

	def update(self):
		"""Update method which should be called every frame to update this manager"""

		if self._attack_time - time.time() < 0 or self._obj.is_dead:
			self._stop_attacks()

		if time.time() - self._attack_time > 0.5:
			self.combo = 0

	def attack(self):
		"""Have this manager do an attack"""

		if self._attack_time - time.time() > 0 or self._obj.is_dead:
			return


		anim, start, end = self.attacks[self.combo]

		for i in self._attack_sensors:
			i.start_attack(self.damage)

		self._obj.animation_lock = self._attacking = True
		self._obj.armature.playAction(anim, start, end, blendin=2)
		self._attack_time = time.time() + (end - start) / 30

		self.combo = (self.combo + 1) % self.max_combo

	def _stop_attacks(self):
		if self._attacking:
			for i in self._attack_sensors:
				i.end_attack()

			self._attacking = self._obj.animation_lock = False



class ProjectileSensor(types.KX_GameObject):
	"""Sensor object that detects collisions for  :class:`.RangeAttackManager`"""

	def __init__(self, start_position, projectile, direction, speed, damage, character):
		"""
		:param start_position: The world position where this sensor is spawned
		:param projectile: The name of the KX_GameObject to use as a projectile (a replica will be added to the scene)
		:param direction: A direction vector the projectile will travel along
		:param speed: How fast the projectile will travel along its direction vector
		:param damage: How much damage the projectile will cause upon impact
		:param character: Ignore this character when doing collision checks
		"""
		self.start_position = self.worldPosition.copy()
		self.direction = direction.normalized()
		self.speed = speed
		self.damage = damage
		self._character = character

		self.collisionCallbacks.append(self._collision)

		self.collisions = set()

	def __new__(cls, start_position, projectile, direction, *args):
		adder = logic.getCurrentController().owner
		scene = logic.getCurrentScene()

		obj = scene.addObject(projectile, adder)

		obj.worldPosition = start_position

		x = direction.cross(Vector((0, 0, 1)))
		x.normalize()

		y = direction.normalized()

		z = x.cross(y)
		z.normalize()

		ori = (
				(x[0], y[0], z[0]),
				(x[1], y[1], z[1]),
				(x[2], y[2], z[2])
			)

		obj.worldOrientation = ori
		return super().__new__(cls, obj)

	def __del__(self):
		self.collisionCallbacks.remove(self.collision)

	def update(self):
		"""Update method which should be called every frame to update this sensor"""
		# Move along the given direction vector with the given speed
		vec = self.direction * self.speed

		# Scale the speed so FPS changes don't mess with movement
		fps = logic.getAverageFrameRate()
		fps_scale = 60 / fps if fps != 0 else 60

		self.worldPosition += vec * fps_scale

	def _collision(self, other):
		if other != self._character and hasattr(other, "hp") and other not in self.collisions:
			other.hp -= self.damage
			self.collisions.add(other)


class RangeAttackManager:
	"""Handles ranged attacks for :class:`.Character` objects"""

	def __init__(self, character, projectile, speed, distance, damage, cooldown):
		"""
		:param character: The :class:`.Character` this manager is attached to
		:param projectile: The name of the KX_GameObject to use as a projectile (a replica will be added to the scene)
		:param speed: How fast the projectile will travel along its direction vector
		:param distance: The maximum range of projectiles
		:param damage: How much damage each hit should cause
		:param cooldown: The duration until this manager can attack again after recently attacking
		"""

		self._obj = character
		self.speed = speed
		self.projectile = projectile
		self.distance = distance ** 2
		self.damage = damage
		self.cooldown = cooldown

		self.projectiles = []
		self._cooldown_timer = time.time()

	def update(self):
		"""Update method which should be called every frame to update this manager"""

		if self._obj.is_dead and self.projectiles:
			# Just kill any airborne projectiles
			for i in self.projectiles:
				i.endObject()
		else:
			for i in self.projectiles[:]:
				i.update()
				if (i.worldPosition - i.start_position).length_squared > self.distance:
					self.projectiles.remove(i)
					i.endObject()


	def attack(self, start_position, direction):
		"""Have this manager do an attack

		:param start_position: The starting position of the projectile
		:param direction: The direction vector of the projectile
		"""

		if self._cooldown_timer > time.time() or self._obj.is_dead:
			return

		self.projectiles.append(ProjectileSensor(start_position, self.projectile, direction, self.speed, self.damage, self._obj))

		self._cooldown_timer = time.time() + self.cooldown


class MouseRangeAttackManager(RangeAttackManager):
	"""A :class:`.RangeAttackManager` that uses the character and mouse as starting positions and directions, respectively, for projectiles"""
	def __init__(self, obj, projectile, speed, distance, damage, cooldown):
		"""
		:param character: The :class:`.Character` this manager is attached to
		:param projectile: The name of the KX_GameObject to use as a projectile (a replica will be added to the scene)
		:param speed: How fast the projectile will travel along its direction vector
		:param distance: The maximum range of projectiles
		:param damage: How much damage each hit should cause
		:param cooldown: The duration until this manager can attack again after recently attacking
		"""

		super().__init__(obj, projectile, speed, distance, damage, cooldown)

		# DEBUGGING
		#adder = logic.getCurrentController().owner
		#scene = logic.getCurrentScene()

		#obj = scene.addObject(projectile, adder)
		#self._aim_ob = obj

	def attack(self):
		"""Have this manager do an attack"""

		# Get start position
		start_position = self._obj.worldPosition

		# Get aim direction
		cam = logic.getCurrentScene().active_camera

		vec = cam.getScreenVect(0.5, 0.5) + cam.worldPosition

		ob, point, norm = cam.rayCast(vec, None, -1000)

		# DEBUGGING
		#if point:
			#self._aim_ob.worldPosition = point

		# Calculate projectile direction
		aim = point - start_position if point else cam.getAxisVect((0, 0, -1))

		super().attack(start_position, aim)
