import sys
import os
import math


from bge import logic, events
from mathutils import Vector, Euler


def init():
	if ".." not in sys.path:
		os.chdir(logic.expandPath("//"))
		sys.path.append("..")

		from scripts.character import UllurCharacter
		logic.character = UllurCharacter.spawn()
		logic.mouse.position = (0.5, 0.5)


def run():
	try:
		logic.character
	except AttributeError:
		init()

	logic.character.update()

	cam = logic.getCurrentScene().active_camera

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

	for event, status in logic.mouse.active_events.items():
		if event == events.LEFTMOUSE and status == logic.KX_INPUT_JUST_ACTIVATED:
			logic.character.attack("LEFT")
		elif event == events.RIGHTMOUSE and status == logic.KX_INPUT_JUST_ACTIVATED:
			logic.character.attack("RIGHT")

	diffx = 0.5 - logic.mouse.position[0]

	if math.fabs(diffx) > 0.01:
		cam.parent.applyRotation((0, 0, diffx))

	logic.mouse.position = (0.5, 0.5)

	cam_vec = cam.getAxisVect((0, 0, -1))
	cam_vec.z = 0
	offset = cam_vec.angle(Vector((0, 1, 0)))
	if cam_vec.x > 0:
		offset *= -1
	offset = Euler((0, 0, offset))
	movevec.rotate(offset)

	logic.character.move(movevec.xy)

