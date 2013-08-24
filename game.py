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
DEFAULTS = {
	'system': {
		'debug': 'false',
		'player_path': 'blenderplayer',
	},

	'window': {
		'fullscreen': 'false',
		'x_resolution': '1600',
		'y_resolution': '900',
		'aasamples': '4',
	},

	'profile': {
		'show_fps': 'false',
		'show_profiler': 'false',
	},

	'game': {
		'dostartup': 'true',
		'level': 'startup',
	},
}

def main():
	config = configparser.ConfigParser()

	if CONFIG_NAME in os.listdir('.'):
		config.read(CONFIG_NAME)

	needs_write = False

	# Make the config safe
	for section, options in DEFAULTS.items():
		if not config.has_section(section):
			config.add_section(section)
			needs_write = True

		for option, value in options.items():
			if not config.has_option(section, option):
				needs_write = True
				config.set(section, option, value)

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

	args.append(os.getcwd() + "/src/levels/%s.blend" % config.get('game', 'level'))

	# All args after '-' are sent to Python
	if config.getboolean('game', 'dostartup'):
		args.append('-')
		args.append('dostartup')

	# Keep PyDev from setting the PYTHONPATH
	env = os.environ.copy()
	if 'PYTHONPATH' in env:
		del env['PYTHONPATH']

	subprocess.call(args, env=env)

	if needs_write:
		with open(CONFIG_NAME, 'w') as f:
			config.write(f)


if __name__ == '__main__':
	main()
