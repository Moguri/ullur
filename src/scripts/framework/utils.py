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


import os
import configparser


__DEFAULT_CONFIG = {
	'paths': {
		'characters': 'characters',
		'levels': 'levels',
	},
}


CONFIG_NAME = 'engine.ini'
__CONFIG = None


def __init_framework_config():
	global __CONFIG

	config = configparser.ConfigParser()

	if CONFIG_NAME in os.listdir('.'):
		config.read(CONFIG_NAME)

	needs_write = False

	# Make the config safe
	for section, options in __DEFAULT_CONFIG.items():
		if not config.has_section(section):
			config.add_section(section)
			needs_write = True

		for option, value in options.items():
			if not config.has_option(section, option):
				needs_write = True
				config.set(section, option, value)

	if needs_write:
		with open(CONFIG_NAME, 'w') as f:
			config.write(f)

	__CONFIG = config


def get_path(type, file):
	if not __CONFIG:
		__init_framework_config()

	return os.path.join(__CONFIG.get('paths', type), file)