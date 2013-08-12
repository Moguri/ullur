from bge import types


from .character import UllurCharacter


class Collectable:
	"""Base collectable class"""
	def __init__(self, character):
		print(self.__class__.__name__, "added to", character)


class CollectableSpeed(Collectable):
	"""Collectable that increases the character's :attr:`.Character.RUN_MULTIPLIER`"""
	def __init__(self, character):
		super().__init__(character)

		character.RUN_MULTIPLIER = 5

class CollectableSensor(types.KX_GameObject):
	"""Sensor that detects collisions for :class:`.Collectable` objects"""

	def __init__(self, gameobj, collectable_list):
		"""
		:param gameobj: The KX_GameObject to mutate (passed on to __new__)
		:param collectable_list: The list this sensor should be stored in
		"""
		self.collisionCallbacks.append(self._collision)
		self.collectable_list = collectable_list

		if self.name.startswith('CollectableSpeed'):
			self.collectable = CollectableSpeed
		else:
			self.collectable = Collectable

	def __new__(cls, gameobj, *args):
		return super().__new__(cls, gameobj)

	def _collision(self, other):
		if isinstance(other, UllurCharacter):
			other.add_collectable(self.collectable(other))
			self.collectable_list.remove(self)

			self.endObject()


def mutate_collectables(objects, collectable_list):
	"""Mutates a list of KX_GameObjects into :class:`.CollectableSensor`

	:param objects: The list of objects to mutate
	:param collectable_list: The list to store the mutated collectables
	"""
	for i in [i for i in objects if i.name.startswith('Collectable')]:
		if i.groupObject:
			collectable_list.append(CollectableSensor(i, collectable_list))
