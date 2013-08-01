import time


from bge import types, logic
from mathutils import Vector

class AttackSensor(types.KX_GameObject):
	def __init__(self, gameobj, character):
		self._character = character
		self.collisionCallbacks.append(self.collision)

		if not hasattr(character, "_attack_hits"):
			character._attack_hits = set()

		self.detect_collisions = False
		self._damage = 0

	@property
	def collisions(self):
		return self._character._attack_hits

	def __new__(cls, gameobj, *args):
		return super().__new__(cls, gameobj)

	def __del__(self):
		self.collisionCallbacks.remove(self.collision)

	def start_attack(self, damage):
		self._damage = damage
		self.detect_collisions = True
		self.collisions.clear()

	def end_attack(self):
		self.detect_collisions = False

	def collision(self, other):
		if not self.detect_collisions:
			return

		if other != self._character and hasattr(other, "hp") and other not in self.collisions:
			self.collisions.add(other)
			other.hp -= self._damage


class MeleeAttackManager:
	def __init__(self, obj, attack_sensors, attacks, damage):
		obj._attack_time = time.time()
		self._attack_sensors = attack_sensors
		self._obj = obj
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
		if self._attack_time - time.time() < 0 or self._obj.is_dead:
			self.stop_attacks()

		if time.time() - self._attack_time > 0.5:
			self.combo = 0

	def attack(self):
		if self._attack_time - time.time() > 0 or self._obj.is_dead:
			return


		anim, start, end = self.attacks[self.combo]

		for i in self._attack_sensors:
			i.start_attack(self.damage)

		self._obj.animation_lock = self._attacking = True
		self._obj.armature.playAction(anim, start, end, blendin=2)
		self._attack_time = time.time() + (end - start) / 30

		self.combo = (self.combo + 1) % self.max_combo

	def stop_attacks(self):
		if self._attacking:
			for i in self._attack_sensors:
				i.end_attack()

			self._attacking = self._obj.animation_lock = False



class ProjectileSensor(types.KX_GameObject):

	def __init__(self, start_position, projectile, direction, speed, damage, character):
		self.start_position = self.worldPosition.copy()
		self.direction = direction.normalized()
		self.speed = speed
		self.damage = damage
		self._character = character

		self.collisionCallbacks.append(self.collision)

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
		# Move along the given direction vector with the given speed
		vec = self.direction * self.speed

		# Scale the speed so FPS changes don't mess with movement
		fps = logic.getAverageFrameRate()
		fps_scale = 60 / fps if fps != 0 else 60

		self.worldPosition += vec * fps_scale

	def collision(self, other):
		if other != self._character and hasattr(other, "hp") and other not in self.collisions:
			other.hp -= self.damage
			self.collisions.add(other)


class RangeAttackManager:
	def __init__(self, obj, projectile, speed, distance, damage, cooldown):
		self._obj = obj
		self.speed = speed
		self.projectile = projectile
		self.distance = distance ** 2
		self.damage = damage
		self.cooldown = cooldown

		self.projectiles = []
		self._cooldown_timer = time.time()

	def update(self):
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


	def attack(self):
		if self._cooldown_timer > time.time() or self._obj.is_dead:
			return

		direction = self._obj.getAxisVect((0, 1, 0))
		start_position = self._obj.worldPosition

		self.projectiles.append(ProjectileSensor(start_position, self.projectile, direction, self.speed, self.damage, self._obj))

		self._cooldown_timer = time.time() + self.cooldown
