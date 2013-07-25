import sys
import os


from bge import logic


def init():
	if ".." not in sys.path:
		sys.path.append("..")
		os.chdir(logic.expandPath("//"))

