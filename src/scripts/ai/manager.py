class Manager:
	def __init__(self):
		self._agents = []
		self._action_set = {}
		self._actions = {}
		self._transitions = {}

		from .actionsets import bge as bge_actions
		for item in dir(bge_actions):
			if not item.startswith("_"):
				self._action_set[item] = getattr(bge_actions, item)
				
		for i, v in self._action_set.items():
			print(i, '=', v)

	def update(self, dt):
		invalid_agents = []
		for agent in self._agents:
			if not agent.valid:
				invalid_agents.append(agent)
				continue

			agent.update_actions(self._action_set)
			agent.update_steering(dt)
			agent.apply_steering()

		for agent in invalid_agents:
			self._agents.remove(agent)