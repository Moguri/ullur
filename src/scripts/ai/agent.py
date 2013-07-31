import mathutils

class Steering:
	def __init__(self):
		self.linear = mathutils.Vector.Fill(3)
		self.angular = 0


def seek(agent):
	output = Steering()
	
	if not agent.target:
		return output

	output.linear = agent.target.position - agent.position
	
	return output
	

class Agent:
	def __init__(self, object=None):
		self.object = object
		self.target = None
		self.max_acceleration = 0.5
		self.max_speed = 0.1
		self.turn_speed = 0.1
		
		self.velocity = mathutils.Vector.Fill(3)
		self.rotation = 0
		
		self.actions = []
		
	def update_actions(self):
		self.actions = [seek]
		
	def update_steering(self, dt):
		linear = mathutils.Vector.Fill(3)
		angular = 0
		count = 0
		
		for action in self.actions:
			output = action(self)
			if output:
				if output.linear:
					linear += output.linear
				if output.angular:
					angular += output.angular
					count += 1
				
		linear.normalize()
		linear *= self.max_acceleration
		
		acceleration = linear * dt
		friction = self.max_speed / self.max_acceleration
		self.velocity += acceleration - friction*self.velocity
		
		if count:
			angular /= count
			if angular > self.turn_speed:
				angular = self.turn_speed
			
	def apply_steering(self):
		pass
		
	@property
	def valid(self):
		return True

class AgentBGE(Agent):
	def __init__(self, object=None):
		Agent.__init__(self, object)
		
	@property
	def position(self):
		return self.object.worldPosition
		
	@property
	def orientation(self):
		return self.object.worldOrientation.to_euler('XYZ')[2]
		
	@property
	def valid(self):
		return not self.object.invalid
		
	def apply_steering(self):
		self.object.applyMovement(self.velocity)
		self.object.applyRotation((0, 0, self.rotation))