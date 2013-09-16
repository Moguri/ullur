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
from . import bgui
from .bgui import bge_utils


class MenuSelectWidget(bgui.Widget):

	class LBRenderer():

		def __init__(self, listbox):
			self.label = bgui.Label(listbox)
			self.listbox = listbox

		def render_item(self, item):
			self.label.text = str(item)

			if item == self.listbox.selected:
				self.label.color = [1, 0, 0, 1]
			else:
				self.label.color = [1, 1, 1, 1]

			return self.label

	def __init__(self, parent, items, size, pos):
		super().__init__(parent, size=size, pos=pos)

		self.items = items
		self.menu = bgui.ListBox(self, items=self.items)
		self.menu.renderer = self.LBRenderer(self.menu)
		self.menu.selected = self.items[0]
		self.idx = 0

	@property
	def selected(self):
		return self.menu.selected

	def down(self):
		self.idx += 1
		if self.idx > len(self.items) - 1:
			self.idx = 0
		self.menu.selected = self.items[self.idx]

	def up(self):
		self.idx -= 1
		if self.idx < 0:
			self.idx = len(self.items) - 1
		self.menu.selected = self.items[self.idx]



class StartupLayout(bge_utils.Layout):

	def __init__(self, sys, data):
		super().__init__(sys, data)

		self.frame = bgui.Frame(self, border=0)
		self.frame.colors = [
					(0.2, 0.2, 0.2, 1),
					(0.2, 0.2, 0.2, 1),
					(0, 0, 0, 1),
					(0, 0, 0, 1)
				]

		bgui.Label(self.frame, text="Ullur", pt_size=72, pos=(0.1, 0.8))

		menu_entries = ["New Game", "Exit"]
		self.menu = MenuSelectWidget(self.frame, items=menu_entries,
										size=[0.85, 0.7], pos=[0.15, 0])

	def menu_down(self):
		self.menu.down()

	def menu_up(self):
		self.menu.up()
