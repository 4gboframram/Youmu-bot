from random import randint
from math import ceil
import sys
class Attack:
	'''
	Base class for attacking moves
	'''
	def __init__(self, power, type_, accuracy):
		self.power=power
		self.type=type_
		self.accuracy=accuracy

	def damage_number(self, ghost1, ghost2):
		attack_stat=ghost1.attack
		defense_stat=ghost2.defense
		level=ghost1.level
		base_speed=ghost1.base_speed
		attacker_type=ghost1.type
		defending_type=ghost2.type
		
		type_modifier=attacker_type^defending_type

		damage=((self.power*attack_stat/defense_stat)*(2*level+10)/250)*type_modifier # base damage of the move before adding STAB, accuracy, and crit
			
		rand_int=randint(1, 100)

		if self.type==attacker_type:
			damage*=1.3 #STAB 

		if rand_int>self.accuracy:
			return ('miss', 0)

		if type_modifier==2:
			return ('super_effective', ceil(damage))
		elif type_modifier=='0.5':
			return ('not_very_effective', ceil(damage))
		

		rand_int=randint(1,100)
		if rand_int< base_speed*100/512:
			return ('crit', ceil(damage*1.5))

		return ('normal', ceil(damage))

	def to_dict(self):
		attributes={
			'name': self.name,
			'power': self.power,
			'type_': self.type,
			'accuracy': self.accuracy
			}
		return attributes

	def __repr__(self):
		return str(self.to_dict())

	def __str__(self):
		return f'{self.name}: \n{self.type} Type,  {self.power} Power'

	def from_string(name, *args):
   		return getattr(sys.modules[__name__], name)(*args)

class Haunt(Attack):
	def __init__(self):
		self.name='Haunt'
		self.power=30
		self.type='Grey'
		self.accuracy=90

class Spook(Attack):
	def __init__(self):
		self.name='Spook'
		self.power=25
		self.type='Grey'
		self.accuracy=100

if __name__=='__main__':
	k=Attack.from_string('Spook')
	print(k.__repr__())
