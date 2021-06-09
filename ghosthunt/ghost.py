import json
from math import floor
import sys
class Ghost:
	'''
	The base class for the Ghost
	'''
	def base_to_value(base, level):
		return floor(base*level/50)+5
	def base_hp_to_value(base, level):
		return floor(base*level/50)+level+10
		
	def __init__(self, species, type_, currentxp, currenthp, base_attack, base_defense, base_speed, base_hp, moves):
		self.species=species
		self.type=type_
		
		self.level=floor(currentxp**(1/3))
		self.currentxp=currentxp
		self.currenthp=currenthp

		self.base_attack=base_attack
		self.base_defense=base_defense
		self.base_speed=base_speed
		self.base_hp=base_hp
		self.moves=moves

		self.maxhp=Ghost.base_hp_to_value()
		self.attack=Ghost.base_to_value(base_attack, self.level)
		self.defense=Ghost.base_to_value(base_defense, self.level)
		self.speed=Ghost.base_to_value(base_speed, self.level)

		self.levelup_moves={}

	def __iter__(self):
		yield 'species', self.species
		yield 'type_', self.type
		yield 'currentxp', self.currentxp
		yield 'currenthp', self.currenthp
		yield 'base_attack', self.base_attack
		yield 'base_defense', self.base_defense
		yield 'base_speed', self.base_speed
		yield 'base_hp', self.base_hp
		yield 'moves', self.moves

	def recalc_stats(self):
		self.maxhp=Ghost.base_hp_to_value()
		self.attack=Ghost.base_to_value(self.base_attack, self.level)
		self.defense=Ghost.base_to_value(self.base_defense, self.level)
		self.speed=Ghost.base_to_value(self.base_speed, self.level)
	
	def levelup(self):
		self.level+=1
		if self.level in self.levelup_moves:
			self.moves.append(self.levelup_moves[self.level])

	def from_string(name, *args):
   		return getattr(sys.modules[__name__], name)(*args)
		#other stuff to do with levelup moves here
	#new random goes here

	def to_json(self):
		return json.dumps(dict(self))

 
if __name__=='__main__':
	ghost=Ghost('bruh', 'red', 100, 0, 1000, 100, 10, 10, 10, ['yooy'])
	print(dict(ghost))
	json_=ghost.to_json()
	print(json_)
	new_ghost=Ghost(**dict(ghost))
	print(dict(new_ghost))
	