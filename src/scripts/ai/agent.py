import mathutils

class Steering:
	def __init__(self):
		self.velocity = mathutils.Vector.Fill(3)
		self.rotation = 0


def seek(agent):
	output = Steering()
	
	if not agent.target:
		return output

	output.velocity = agent.target.position - agent.position
	
	return output
	

class Agent:
	def __init__(self, object=None):
		self.object = object
		self.target = None
		self.move_speed = 0.1
		self.turn_speed = 0.1
		self.steering = Steering()
		
		self.actions = []
		
	def update_actions(self):
		self.actions = [seek]
		
	def update_steering(self):
		self.steering.velocity = mathutils.Vector.Fill(3)
		self.steering.rotation = 0
		count = 0
		
		for action in self.actions:
			output = action(self)
			if output:
				self.steering.velocity += output.velocity
				self.steering.rotation += output.rotation
				
		self.steering.velocity.normalize()
		self.steering.velocity *= self.move_speed
		
		if count:
			self.steering.rotation /= count
			if self.steering.rotation > self.turn_speed:
				self.steering.rotation = self.turn_speed
			
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
		self.object.applyMovement(self.steering.velocity)
		self.object.applyRotation((0, 0, self.steering.rotation))