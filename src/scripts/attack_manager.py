import time


from bge import types

class AttackSensor(types.KX_GameObject):
	def __init__(self, gameobj, character):
		types.KX_GameObject.__init__(gameobj)

		self._character = character
		self.collisionCallbacks.append(self.collision)

		if not hasattr(character, "_attack_hits"):
			character._attack_hits = set()

		self.detect_collisions = False
		self._damage = 0

	@property
	def collisions(self):
		return self._character._attack_hits

	def __new__(cls, gameobj, character):
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
	def __init__(self, obj, attack_sensors, attacks):
		obj._attack_time = time.time()
		self._attack_sensors = attack_sensors
		self._obj = obj
		self._attacking = False
		self.combo = 0

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

	def attack(self, damage):
		if self._attack_time - time.time() > 0 or self._obj.is_dead:
			return


		anim, start, end = self.attacks[self.combo]

		for i in self._attack_sensors:
			i.start_attack(damage)

		self._obj.animation_lock = self._attacking = True
		self._obj.armature.playAction(anim, start, end, blendin=2)
		self._attack_time = time.time() + (end - start) / 30

		self.combo = (self.combo + 1) % self.max_combo

	def stop_attacks(self):
		if self._attacking:
			for i in self._attack_sensors:
				i.end_attack()

			self._attacking = self._obj.animation_lock = False