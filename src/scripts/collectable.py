from bge import types


from .character import UllurCharacter

class CollectableSensor(types.KX_GameObject):
	def __init__(self, gameobj):
		self.collisionCallbacks.append(self.collision)

	def __new__(cls, gameobj, *args):
		return super().__new__(cls, gameobj)

	def collision(self, other):
		if isinstance(other, UllurCharacter):
			other.add_collectable(self)

			self.endObject()


def mutate_collectables(objects):
	collectables = []
	for i in [i for i in objects if i.name.startswith('Collectable')]:
		if i.groupObject:
			collectables.append(CollectableSensor(i))

	return collectables