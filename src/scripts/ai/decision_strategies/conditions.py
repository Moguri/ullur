

def get_condition(args):
	return COND_MAP[args[0]](*args[1:])


class ValueCondition:
	__slots__ = ["property", "min", "max"]

	def __init__(self, prop, _min, _max):
		self.property = prop

		if type(_min) == str:
			_min = float(_min)
		if type(_max) == str:
			_max = float(_max)

		self.min = _min
		self.max = _max

	def test(self, agent):
		return self.min < getattr(agent, self.property) < self.max

COND_MAP = {
		"VALUE" : ValueCondition,
	}
