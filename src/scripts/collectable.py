from bge import types


from .character import UllurCharacter


class Collectable:
	pass

class CollectableSensor(types.KX_GameObject):
	def __init__(self, gameobj, collectable_list):
		self.collisionCallbacks.append(self.collision)
		self.collectable = Collectable
		self.collectable_list = collectable_list

	def __new__(cls, gameobj, *args):
		return super().__new__(cls, gameobj)

	def collision(self, other):
		if isinstance(other, UllurCharacter):
			other.add_collectable(self.collectable())
			self.collectable_list.remove(self)

			self.endObject()


def mutate_collectables(objects, collectable_list):
	for i in [i for i in objects if i.name.startswith('Collectable')]:
		if i.groupObject:
			collectable_list.append(CollectableSensor(i, collectable_list))
