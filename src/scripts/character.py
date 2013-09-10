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


from .framework.character import Character
from .attack_manager import AttackSensor, MeleeAttackManager, MouseRangeAttackManager

from bge import logic


class Enemy(Character):
	"""A character sublcass to handle generic enemy logic."""
	DROP = None  #: The name of the item to drop (note, this must be in an inactive layer)

	def handle_drop(self):
		"""Spawn an instance of :attr:`Enemy.DROP` if it is set"""
		if self.DROP:
			return logic.getCurrentScene().addObject(self.DROP, self)


class Meatsack(Enemy):
	"""A character subclass for the Meatsack enemies"""
	MESH = "Cosbad"  #: See :attr:`Character.MESH`


	#: See :attr:`.Character.ANIMATIONS`
	ANIMATIONS = {
				"move": [{'name':'RunBase', 'start_frame':1, 'end_frame':20}, {'name':'RunTop', 'start_frame':1, 'end_frame':20}],
				"idle": [{'name':'IdleBase', 'start_frame':1, 'end_frame':220}, {'name':'IdleTop', 'start_frame':1, 'end_frame':300}],
				"jump": [{'name':'JumpLoop', 'start_frame':1, 'end_frame':30}],
				"dead": [{'name':'Dance', 'start_frame':1, 'end_frame':71}],
				}

	MELEE_ATTACK = [
			('SliceVertical', 1, 16),
		]

	def __init__(self, gameobj):
		super().__init__(gameobj)

		attack_sensors = [AttackSensor(i, self) for i in self.childrenRecursive if i.name.startswith('AttackSensor')]
		self.attack_manager = MeleeAttackManager(self, attack_sensors, self.MELEE_ATTACK, 5)

	def update(self):
		"""See :func:`.Character.update`"""
		self.attack_manager.update()
		super().update()

	def attack(self):
		"""Makes the character perform a melee attack"""
		self.attack_manager.attack()


class Ghost(Enemy):
	MESH = "Ghost"


class Wolf(Enemy):
	MESH = "Wolf"


class Werewolf(Enemy):
	MESH = "Werewolf"
	DROP = "CollectableDrop"


def spawn_baddies(objects, baddies_list):
	"""Spawns enemies at spawn objects

	:param objects: The list of spawn objects
	:param baddies_list: The list to store the spawned enemies
	"""
	for i in [i for i in objects if "spawn" in i.name.lower()]:
		cls = i.name.lower().replace("spawn", "").title()
		baddies_list.append(globals()[cls].spawn(i.worldPosition, i.worldOrientation))


class UllurCharacter(Character):
	"""A character subclass for the player controlled character"""
	MESH = "Sinbad"  #: See :attr:`Character.MESH`

	#: See :attr:`.Character.ANIMATIONS`
	ANIMATIONS = {
				"move": [{'name':'RunBase', 'start_frame':1, 'end_frame':20}, {'name':'RunTop', 'start_frame':1, 'end_frame':20}],
				"idle": [{'name':'IdleBase', 'start_frame':1, 'end_frame':220}, {'name':'IdleTop', 'start_frame':1, 'end_frame':300}],
				"jump": [{'name':'JumpLoop', 'start_frame':1, 'end_frame':30}],
				"dead": [{'name':'Dance', 'start_frame':1, 'end_frame':71}],
				}

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
			self.left_attack_manager.attack()
		else:
			self.right_attack_manager.attack()

	def add_collectable(self, collectable):
		"""Adds a :class:`.Collectable` to the character

		:param collectable: The :class:`.Collectable` to add
		"""
		if collectable not in self.collectables:
			self.collectables.append(collectable)
