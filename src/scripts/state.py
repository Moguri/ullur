class StateSystem:
	def __init__(self, initial_state):
		self.state = initial_state()

	def update(self):
		next_state = self.state.update()
		if next_state:
			if hasattr(self.state, "cleanup"):
				self.state.cleanup()
			self.state = next_state()


# Try to keep Ullur specific stuff below this line to make it easier to separate later
import math
from bge import logic, events
from mathutils import Vector, Euler
from .character import UllurCharacter, Meatsack
from .ai.manager import Manager
from .ai.agent_bge import AgentBGE
from .collectable import CollectableSensor


class DefaultState:
	CAM_MAX_DIST = 9
	CAM_MIN_DIST = 7
	CAM_DOWN_LIMIT = 0.5
	CAM_UP_LIMIT = -1.1

	def __init__(self):
		self.character = UllurCharacter.spawn()

		self.meatsacks = []
		for i in [i for i in logic.getCurrentScene().objects if i.name.startswith('MeatsackSpawn')]:
			self.meatsacks.append(Meatsack.spawn(i.worldPosition, i.worldOrientation))

		self.ai_system = Manager()
		target = AgentBGE(self.character)
		for meatsack in self.meatsacks:
			agent = AgentBGE(meatsack)
			agent.target = target
			agent.load_definition("../scripts/ai/definitions/state_test.json")
			self.ai_system._agents.append(agent)

		self.collectables = []
		for i in [i for i in logic.getCurrentScene().objects if i.name.startswith('Collectable')]:
			if i.groupObject:
				self.collectables.append(CollectableSensor(i))

		logic.mouse.position = (0.5, 0.5)

	def update(self):
		self.character.update()

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
				self.character.jump()

		for event, status in logic.mouse.active_events.items():
			if event == events.LEFTMOUSE and status == logic.KX_INPUT_JUST_ACTIVATED:
				self.character.attack("LEFT")
			elif event == events.RIGHTMOUSE and status == logic.KX_INPUT_JUST_ACTIVATED:
				self.character.attack("RIGHT")

		dx = 0.5 - logic.mouse.position[0]
		dy = 0.5 - logic.mouse.position[1]

		if cam.parent:
			# X Movement
			if math.fabs(dx) > 0.01:
				cam.parent.applyRotation((0, 0, dx))

			# Y Movement
			cam_angle = cam.parent.localOrientation.to_euler('XYZ')
			move_down_limit = dy > 0 and cam_angle.x < self.CAM_DOWN_LIMIT
			move_up_limit = dy < 0 and cam_angle.x > self.CAM_UP_LIMIT
			if math.fabs(dy) > 0.01 and (move_down_limit or move_up_limit):
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
		offset = cam_vec.angle(Vector((0, 1, 0)))
		if cam_vec.x > 0:
			offset *= -1
		offset = Euler((0, 0, offset))
		movevec.rotate(offset)

		self.character.move(movevec.xy)

		dt = 1 / logic.getAverageFrameRate()
		if self.ai_system:
			self.ai_system.update(dt)

		# Update meatsacks
		for i in self.meatsacks[:]:
			i.update()
			if i.is_dead:
				self.meatsacks.remove(i)
				i.endObject()

		if len(self.collectables) == len(self.character.collectables):
			self.collectables = []
			print("All collectibles gathered.")


