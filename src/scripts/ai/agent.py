class Agent:
	def __init__(self, object=None):
		self.object = object
		self.target = None

		self.linear = [0, 0, 0]
		self.angular = 0

		self.actions = []

	def update_actions(self, action_table):
		actions = ['seek']
		
		self.actions = []
		for action in actions:
			self.actions.append(action_table[action])

	def update_steering(self, dt):
		linear = [0, 0, 0]
		angular = 0
		lcount = 0
		acount = 0

		for action in self.actions:
			output = action(self)
			if output:
				if output.linear:
					self.linear[0] += output.linear[0]
					self.linear[1] += output.linear[1]
					self.linear[2] += output.linear[2]
					lcount += 1
				if output.angular:
					self.angular += output.angular
					acount += 1

		if lcount:
			self.linear[0] /= lcount
			self.linear[1] /= lcount
			self.linear[2] /= lcount

		if acount:
			self.angular /= acount

	def apply_steering(self, dt):
		pass

	@property
	def valid(self):
		return True
