import sys
import os


from bge import logic, events
from mathutils import Vector


def init():
	if ".." not in sys.path:
		os.chdir(logic.expandPath("//"))
		sys.path.append("..")

		from scripts.character import Character
		logic.character = Character.spawn()


def run():
	try:
		logic.character
	except AttributeError:
		init()

	logic.character.update()

	movevec = Vector((0, 0))

	for key, status in logic.keyboard.active_events.items():
		if key == events.WKEY:
			movevec += Vector((0, 1))
		elif key == events.AKEY:
			movevec += Vector((-1, 0))
		elif key == events.SKEY:
			movevec += Vector((0, -1))
		elif key == events.DKEY:
			movevec += Vector((1, 0))

	logic.character.move(movevec)

