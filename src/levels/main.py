import sys
import os
import math


from bge import logic, events
from mathutils import Vector, Euler


CAM_MAX_DIST = 9
CAM_MIN_DIST = 7
CAM_DOWN_LIMIT = 0.5
CAM_UP_LIMIT = -1.1


def init():
	if ".." not in sys.path:
		os.chdir(logic.expandPath("//"))
		sys.path.append("..")

		try:
			from scripts.character import UllurCharacter, Meatsack
			logic.character = UllurCharacter.spawn()

			logic.meatsacks = []
			for i in [i for i in logic.getCurrentScene().objects if i.name.startswith('MeatsackSpawn')]:
				logic.meatsacks.append(Meatsack.spawn(i.worldPosition, i.worldOrientation))
		except:
			import traceback
			traceback.print_exc()
			logic.character = None
		logic.mouse.position = (0.5, 0.5)


def run():
	try:
		logic.character
	except AttributeError:
		init()

	if not logic.character:
		return

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

	if cam.parent:
		# X Movement
		if math.fabs(dx) > 0.01:
			cam.parent.applyRotation((0, 0, dx))

		# Y Movement
		cam_angle = cam.parent.localOrientation.to_euler('XYZ')
		move_down_limit = dy > 0 and cam_angle.x < CAM_DOWN_LIMIT
		move_up_limit = dy < 0 and cam_angle.x > CAM_UP_LIMIT
		if math.fabs(dy) > 0.01 and (move_down_limit or move_up_limit):
			cam.parent.applyRotation((dy/2, 0, 0), True)

		# Zoom in camera based on y movement
		if cam_angle.x > 0:
			fac = cam_angle.x / CAM_DOWN_LIMIT
			cam.localPosition.y = -((CAM_MAX_DIST - CAM_MIN_DIST) * (1 - fac) + CAM_MIN_DIST)
		else:
			cam.localPosition.y = -CAM_MAX_DIST

	logic.mouse.position = (0.5, 0.5)

	cam_vec = cam.getAxisVect((0, 0, -1))
	cam_vec.z = 0
	offset = cam_vec.angle(Vector((0, 1, 0)))
	if cam_vec.x > 0:
		offset *= -1
	offset = Euler((0, 0, offset))
	movevec.rotate(offset)

	logic.character.move(movevec.xy)


	# Update meatsacks
	for i in logic.meatsacks[:]:
		i.update()
		if i.is_dead:
			logic.meatsacks.remove(i)
			i.endObject()

