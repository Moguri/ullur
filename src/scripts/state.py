class StateSystem:
	def __init__(self, initial_state):
		self.state = initial_state()

	def update(self):
		next_state = self.state.update()
		if next_state:
			if hasattr(self.state, "cleanup"):
				self.state.cleanup()
			self.state = next_state()


class DefaultState:
	def update(self):
		print("Update")

