import sys
import os


from bge import logic


def init():
	if ".." not in sys.path:
		os.chdir(logic.expandPath("//"))
		sys.path.append("..")

		from scripts.character import Character
		logic.character = Character.spawn()


def run():
	try:
		logic.character.update()
	except AttributeError:
		init()
