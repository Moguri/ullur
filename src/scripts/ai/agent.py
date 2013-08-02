from .decision_strategies.state_machine import StateMachine



STRATEGIES = {
	"STATE_MACHINE" : StateMachine
	}


STRATEGIES_INV = {v : k for k, v in STRATEGIES.items()}


class Agent:
	def __init__(self, object=None, definition=None):
		self.object = object
		self.target = None

		self.linear = [0, 0, 0]
		self.angular = 0

		self.actions = []


		self._decstrat = None
		self.decision_strategy = "STATE_MACHINE"

		if definition:
			self.load_definition(definition)

	@property
	def decision_strategy(self):
		return STRATEGIES_INV[type(self._decstrat)]

	@decision_strategy.setter
	def decision_strategy(self, value):
		if value not in STRATEGIES:
			raise ValueError(value, "is not a valid decision strategy.", \
				"Valid strategies are: %s" % str(STRATEGIES.keys()))

		self._decstrat = STRATEGIES[value]()

	def load_definition(self, data):
		if self._decstrat:
			self._decstrat.load(data)
			return

		raise AttributeError("Agent has no decision strategy set")


	def update_actions(self, action_table):
		actions = []
		if self._decstrat:
			actions = self._decstrat()

		self.actions = []
		for action in actions:
			self.actions.append(action_table[action])

	def update_steering(self, dt):
		self.linear = [0, 0, 0]
		self.angular = 0
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

		if lcount > 1:
			self.linear[0] /= lcount
			self.linear[1] /= lcount
			self.linear[2] /= lcount

		if acount > 1:
			self.angular /= acount

	def apply_steering(self, dt):
		pass

	@property
	def valid(self):
		return True
