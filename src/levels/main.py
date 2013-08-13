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

import sys
import os

from bge import logic


def init():
	if ".." not in sys.path:
		os.chdir(logic.expandPath("//"))
		sys.path.append("..")

		try:
			from scripts.state import DefaultState
			from scripts.framework.state import StateSystem
			logic.state_system = StateSystem(DefaultState)
		except:
			import traceback
			traceback.print_exc()
			logic.state_system = None


def run():
	try:
		logic.state_system
	except AttributeError:
		init()

	if not logic.state_system:
		return

	logic.state_system.update()


