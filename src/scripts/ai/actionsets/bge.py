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
	output.linear.normalize()
	output.linear *= agent.max_acceleration

	return output