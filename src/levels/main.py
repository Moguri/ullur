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

	cam = logic.getCurrentScene().active_camera
	cam_mat = cam.worldOrientation

	movevec = Vector((0, 0, 0))

	for key, status in logic.keyboard.active_events.items():
		if key == events.WKEY:
			movevec += Vector((0, 1, 0))
		elif key == events.AKEY:
			movevec += Vector((-1, 0, 0))
		elif key == events.SKEY:
			movevec += Vector((0, -1, 0))
		elif key == events.DKEY:
			movevec += Vector((1, 0, 0))
		elif key == events.SPACEKEY and status == logic.KX_INPUT_JUST_ACTIVATED:
			logic.character.jump()

	logic.character.move(movevec.normalized().xy)

