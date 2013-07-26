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

	dx = 0.5 - logic.mouse.position[0]
	dy = 0.5 - logic.mouse.position[1]

	# X Movement
	if math.fabs(dx) > 0.01:
		cam.parent.applyRotation((0, 0, dx))

	# Y Movement
	cam_angle = cam.parent.localOrientation.to_euler('XYZ')
	move_down_limit = dy > 0 and cam_angle.x < 0.5
	move_up_limit = dy < 0 and cam_angle.x > -1.1
	if math.fabs(dy) > 0.01 and (move_down_limit or move_up_limit):
		cam.parent.applyRotation((dy/2, 0, 0), True)

	logic.mouse.position = (0.5, 0.5)

	cam_vec = cam.getAxisVect((0, 0, -1))
	cam_vec.z = 0
	offset = cam_vec.angle(Vector((0, 1, 0)))
	if cam_vec.x > 0:
		offset *= -1
	offset = Euler((0, 0, offset))
	movevec.rotate(offset)

	logic.character.move(movevec.xy)

