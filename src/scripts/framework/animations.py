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


from bge import logic


class AnimationManager:
	"""A manager that handles :class:`.AnimationState` objects and transitioning between them"""

	MAX_LAYERS = 8
	DEFAULTS = {
		'priority': 0,
		'blendin': 3,
		'play_mode': logic.KX_ACTION_MODE_LOOP,
		'blend_mode': logic.KX_ACTION_BLEND_ADD,
		'layer_weight': 1,
		'speed': 1,
	}

	def __init__(self, character, initial_state):
		self.character = character
		self.current_state = initial_state(character)

	def update(self):
		anim_list = self.current_state.update()

		if not anim_list:
			return

		obj = self.character.armature

		for layer, anim in enumerate(anim_list):
			if anim:
				anim['layer'] = layer

			for k,v in self.DEFAULTS.items():
				if k not in anim:
					anim[k] = v
			obj.playAction(**anim)

		for i in range(layer+1, self.MAX_LAYERS):
			obj.stopAction(i)

	def change_state(self, state):
		if not self.current_state.lock_state:
			self.current_state = state(self.character)

		return self.current_state


class AnimationState:
	"""Determines which animations to play and how to blend them"""

	def __init__(self, character):
		self.character = character
		self.lock_state = False

	def update(self):
		return []
