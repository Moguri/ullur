import sys
import os

from bge import logic


def init():
	if ".." not in sys.path:
		os.chdir(logic.expandPath("//"))
		sys.path.append("..")

		try:
			from scripts.state import StateSystem, DefaultState
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


