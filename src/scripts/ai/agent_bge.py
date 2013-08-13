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

import mathutils


from .agent import Agent


class AgentBGE(Agent):
	'''
	A prebuilt Agent class for use with the Blender Game Engine.
	The forward vector is assumed to be +Y
	'''
	def __init__(self, object=None):
		Agent.__init__(self, object)

		self.max_acceleration = 0.5
		self.max_speed = 0.1
		self.turn_speed = 0.1
		
		self.velocity = mathutils.Vector.Fill(3)
		
	@property
	def target_range(self):
		return (self.target.position - self.position).length

	@property
	def position(self):
		return self.object.worldPosition

	@property
	def orientation(self):
		return self.object.worldOrientation.to_euler('XYZ')[2]

	@property
	def valid(self):
		return not self.object.invalid

	def apply_steering(self, dt):
		self.linear = mathutils.Vector(self.linear)

		acceleration = self.linear * dt
		friction = self.max_acceleration * dt / self.max_speed
		self.velocity += acceleration - friction*self.velocity

		if self.angular > self.turn_speed:
			self.angular = self.turn_speed

		self.object.applyMovement(self.velocity)
		self.object.applyRotation((0, 0, self.angular))