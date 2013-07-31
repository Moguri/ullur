import mathutils as _math


class _Steering:
	def __init__(self):
		self.linear = _math.Vector.Fill(3)
		self.angular = 0


def seek(agent):
	output = _Steering()

	if not agent.target:
		return output

	output.linear = agent.target.position - agent.position

	return output