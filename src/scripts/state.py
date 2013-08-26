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

import math
import sys
from bge import logic, events
from mathutils import Vector, Euler
from .character import UllurCharacter, spawn_baddies
from .ai.manager import Manager
from .ai.agent_bge import AgentBGE
from .collectable import mutate_collectables
from .framework import utils


class StartupState:
	"""Handles displaying the main menu and launching the level"""

	#  The "//../" is to get LibLoad to be happy, we should find a better fix at some point
	MAIN_LEVEL = "//../"+utils.get_path('levels', 'test_grounds.blend')

	def update(self):
		"""Called by the :class:`.StateSystem` to run this state"""

		logic.LibLoad(self.MAIN_LEVEL, 'Scene')

		# Remove any non-startup mains, but move the adder
		ob = logic.getCurrentController().owner
		for i in [i for i in logic.getCurrentScene().objects if i.name.startswith("main")]:
			if i != ob:
				ob.worldPosition = i.worldPosition
				i.endObject()


		return DefaultState

class DefaultState:
	"""Ullur's main state"""

	CAM_MAX_DIST = 9  #: The maximum follow distance for the camera
	CAM_MIN_DIST = 7  #: The minimum follow distance for the camera
	CAM_DOWN_LIMIT = 0.5  #: The maximum angle of the camera relative to the horizontal (faces into the ground)
	CAM_UP_LIMIT = -1.1  #: The minimum angle of the camera relative to the horizontal (faces into the sky)

	def __init__(self):
		self.character = UllurCharacter.spawn()
		
		object_list = logic.getCurrentScene().objects

		self.meatsacks = []
		spawn_baddies(object_list, self.meatsacks)

		self.ai_system = Manager()
		target = AgentBGE(self.character)
		for meatsack in self.meatsacks:
			agent = AgentBGE(meatsack)
			agent.target = target
			agent.load_definition("scripts/ai/definitions/state_test.json")
			self.ai_system._agents.append(agent)

		self.collectables = []
		mutate_collectables(object_list, self.collectables)

		logic.mouse.position = (0.5, 0.5)

	def update(self):
		"""Called by the :class:`.StateSystem` to run this state"""
		self.character.update()

		cam = logic.getCurrentScene().active_camera

		movevec = Vector((0, 0, 0))
		self.character.running = False

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
				self.character.jump()
			elif key == events.LEFTSHIFTKEY:
				self.character.running = True

		for event, status in logic.mouse.active_events.items():
			if event == events.LEFTMOUSE and status == logic.KX_INPUT_JUST_ACTIVATED:
				self.character.attack("LEFT")
			elif event == events.RIGHTMOUSE and status == logic.KX_INPUT_JUST_ACTIVATED:
				self.character.attack("RIGHT")

		dx = 0.5 - logic.mouse.position[0]
		dy = 0.5 - logic.mouse.position[1]

		if cam.parent:
			# X Movement
			if math.fabs(dx) > 0.0001:
				cam.parent.applyRotation((0, 0, dx))

			# Y Movement
			cam_angle = cam.parent.localOrientation.to_euler('XYZ')
			move_down_limit = dy > 0 and cam_angle.x < self.CAM_DOWN_LIMIT
			move_up_limit = dy < 0 and cam_angle.x > self.CAM_UP_LIMIT
			if math.fabs(dy) > 0.0001 and (move_down_limit or move_up_limit):
				cam.parent.applyRotation((dy/2, 0, 0), True)

			# Zoom in camera based on y movement
			if cam_angle.x > 0:
				fac = cam_angle.x / self.CAM_DOWN_LIMIT
				cam.localPosition.y = -((self.CAM_MAX_DIST - self.CAM_MIN_DIST) * (1 - fac) + self.CAM_MIN_DIST)
			else:
				cam.localPosition.y = -self.CAM_MAX_DIST

		logic.mouse.position = (0.5, 0.5)

		cam_vec = cam.getAxisVect((0, 0, -1))
		cam_vec.z = 0

		if cam_vec.length_squared != 0:
			offset = cam_vec.angle(Vector((0, 1, 0)))
			if cam_vec.x > 0:
				offset *= -1
			offset = Euler((0, 0, offset))
			movevec.rotate(offset)

		self.character.move(movevec.xy)

		if logic.getAverageFrameRate():
			dt = 1 / logic.getAverageFrameRate()
		else:
			dt = 0
		if self.ai_system:
			self.ai_system.update(dt)

		# Update meatsacks
		for i in self.meatsacks[:]:
			i.update()
			if i.is_dead:
				self.meatsacks.remove(i)
				i.endObject()

		if self.collectables is not None and len(self.collectables) == 0:
			self.collectables = None
			print("All collectables gathered.")


