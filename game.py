#!/usr/bin/python

import subprocess
import os
try:
	import configparser
except ImportError:
	import ConfigParser as configparser
import sys
from collections import OrderedDict

CONFIG_NAME = "config.ini"


def main():
	config = configparser.ConfigParser()

	if CONFIG_NAME in os.listdir('.'):
		config.read(CONFIG_NAME)
	else:
		config.add_section('system')
		config.set('system', 'debug', 'false')
		config.set('system', 'player_path', 'blenderplayer')

		config.add_section('window')
		config.set('window', 'fullscreen', 'false')
		config.set('window', 'x_resolution', '1600')
		config.set('window', 'y_resolution', '900')
		config.set('window', 'aasamples', '4')

		config.add_section('profile')
		config.set('profile', 'show_fps', 'false')
		config.set('profile', 'show_profiler', 'false')

		with open(CONFIG_NAME, 'w') as f:
			config.write(f)

	args = [config.get('system', 'player_path')]

	args.append('-f' if config.getboolean('window', 'fullscreen') else '-w')
	args.append(config.get('window', 'x_resolution'))
	args.append(config.get('window', 'y_resolution'))
	args.append('-m')
	args.append(config.get('window', 'aasamples'))

	if config.getboolean('profile', 'show_fps'):
		args.extend("-g show_framerate = 1".split())
	if config.getboolean('profile', 'show_profiler'):
		args.extend("-g show_profile = 1".split())
	if config.getboolean('system', 'debug'):
		args.append("-c")

	args.append(os.getcwd() + "/src/levels/test_grounds.blend")

	# Keep PyDev from setting the PYTHONPATH
	env = os.environ.copy()
	if 'PYTHONPATH' in env:
		del env['PYTHONPATH']
	#env['PYTHONHOME'] = "/home/mitchell/blender-dev/trunk/build/bin/2.66/python"

	subprocess.call(args, env=env)


if __name__ == '__main__':
	main()
