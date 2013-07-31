class Manager:
	def __init__(self):
		self._agents = []
		self._actions = {}
		self._transitions = {}
		
	def update(self, dt):
		invalid_agents = []
		for agent in self._agents:
			if not agent.valid:
				invalid_agents.append(agent)
				continue

			agent.update_actions()
			agent.update_steering(dt)
			agent.apply_steering()

		for agent in invalid_agents:
			self._agents.remove(agent)