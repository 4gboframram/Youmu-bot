class InvalidTypeError(Exception): #used for debugging
	def __init__(self, type_):
		self.message=f"Invalid type, {type_}!" 
class GhostType:
	'''
	List of ghost types:

	Grey, Red, Yellow, Green, Blue
	'''
	def __init__(self, name):
		self.name=name

	def __xor__(self, other): #type effectiveness
		type1=self.name #attacking type
		type2=other.name #defending type

		if type1=='red': #I wish python 3.8 had match
			if type2=='red': 
				return 0.5
			elif type2=='yellow':
				return 1
			elif type2=='blue':
				return 0.5
			elif type2=='green':
				return 2
			elif type2=='grey':
				return 2
			else: raise InvalidTypeError(type2)
		elif type1=='yellow': #I wish python 3.8 had match
			if type2=='red': 
				return 1
			elif type2=='yellow':
				return 2
			elif type2=='blue':
				return 2
			elif type2=='green':
				return 1
			elif type2=='grey':
				return 1
			else: raise InvalidTypeError(type2)
		elif type1=='blue': #I wish python 3.8 had match
			if type2=='red': 
				return 2
			elif type2=='yellow':
				return 1
			elif type2=='blue':
				return 0.5
			elif type2=='green':
				return 0.5
			elif type2=='grey':
				return 2
			else: raise InvalidTypeError(type2)
		elif type1=='green': #I wish python 3.8 had match
			if type2=='red': 
				return 0.5
			elif type2=='yellow':
				return 2
			elif type2=='blue':
				return 2
			elif type2=='green':
				return 1
			elif type2=='grey':
				return 0.5
			else: raise InvalidTypeError(type2)
		elif type1=='grey': #I wish python 3.8 had match
			if type2=='red': 
				return 1
			elif type2=='yellow':
				return 1
			elif type2=='blue':
				return 1
			elif type2=='green':
				return 0.5
			elif type2=='grey':
				return 2
			else: raise InvalidTypeError(type2)
		else: raise InvalidTypeError(type1)


if __name__=='__main__':
	print(GhostType('grey')^GhostType('green'))