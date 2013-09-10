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
