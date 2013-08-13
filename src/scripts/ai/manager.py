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

		# for i, v in self._action_set.items():
			# print(i, '=', v)

	def update(self, dt):
		invalid_agents = []
		for agent in self._agents:
			if not agent.valid:
				invalid_agents.append(agent)
				continue

			agent.update_actions(self._action_set)
			agent.update_steering(dt)
			agent.apply_steering(dt)

		for agent in invalid_agents:
			self._agents.remove(agent)