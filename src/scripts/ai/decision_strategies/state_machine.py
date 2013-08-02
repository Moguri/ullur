class State:
	__slots__ = ["actions", "entry_actions", "exit_actions", "transitions"]
	
	def __init__(self, actions, entry_actions, exit_actions, transitions):
		self.actions = actions
		self.entry_actions = entry_actions
		self.exit_actions = exit_actions
		self.transitions = transitions


class Transition:
	__slots__ = ["condition", "state"]

	def __init__(self, condition, state):
		self.condition = condition
		self.state = state


class StateMachine:
	def __init__(self):
		self.states = {}
		self.current_state = None

	def load(self, data):
		# Load states
		for state in data["states"]:
			actions = state["actions"]
			entry_actions = state["entry_actions"]
			exit_actions = state["exit_actions"]

			transitions = []
			for transition in state["transitions"]:
				condition = transition[0]
				target_state = transition[1]
				transitions.append(Transition(condition, target_state))

			self.states[state["name"]] = State(actions, entry_actions,\
				exit_actions, transitions)

		# Link transitions
		for state in self.states.values():
			for transition in state.transitions:
				transition.state = self.states[transition.state]

	def __call__(self):	
		return ["seek"]
