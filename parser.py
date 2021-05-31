#import os
#import discord
#import asyncio
import ply.lex as lex
import ply.yacc as yacc
from actions import Ban, Mute, Rp, Perm, Delete, Color, Lock, Clear, Rate, Percent

"""reserved={
	#'rate': 'RATE'
	
}"""
tokens=[
	'MEMBER', 'CHANNEL', 'ROLE', 'PERMISSION', 'EXTEND', 'REDUCT', 'INT', 'TIME', 'COLOR', #'ID'
] #+ list(reserved.values())

t_ignore  = ' \t'
t_PERMISSION=r'[a-zA-Z_]+'
t_EXTEND=r'\+'
t_REDUCT=r'\-'
t_ignore_COMMENT = r';.*'


"""def t_ID(t):
     r'[a-zA-Z_][a-zA-Z_0-9]*'
     t.type = reserved.get(t.value,'ID')    # Check for reserved words
     print(t)
     return t"""
def t_TIME(t):
	r'\d+[smhd]'
	val=int(t.value[0:len(t.value)-1])
	if 'm' in t.value:
		val*=60
	elif 'h' in t.value:
		val*=60*60
	elif 'd' in t.value:
		val*=60*60*24
	t.value=val
	return t
def t_COLOR(t):
	r'[a-fA-F\d]{6}'
	t.value=int('0x'+t.value, 16)
	return t

def t_INT(t):
	r'\d+'
	t.value=int(t.value)
	return t
def t_MEMBER(t):
	r'<@\!?\d+>'
	t.value=t.value.replace('<@', '').replace('>','')
	if '!' in t.value:
		t.value=(int(t.value.replace('!','')), 'member')
	else: t.value=(int(t.value), 'member',)
	return t

def t_CHANNEL(t):
	r'<\#\d+>'
	t.value=(int(t.value.replace('<#', '').replace('>','')), 'channel')
	return t

def t_ROLE(t):
	r'<@&\d+>'
	t.value=(int( t.value.replace('<@&', '').replace('>','')), 'role',)
	return t

"""def t_STRING(t):
	r'\".*\"'
	t.value=t.value.replace('"', '')
	return t"""
def t_error(t):
	print(t)
	t.lexer.skip(1)
	return t


"""def t_eof(t):
	# Get more input (Example)
	more = input('... ')
	if more:
		lexer.input(more)
		return lexer.token()
	return None"""
class CommandSyntaxError(Exception): 
	def __init__(self, line, pos, token):
		self.message=f"Syntax Error in line `{line}` at position `{pos}`: `{token}`"
		super().__init__(self.message)
class CommandUnexpectedEOF(Exception):
	def __init__(self):
		self.message=f"Unexpected EOF while parsing command"
		super().__init__(self.message)

results=[]
def p_command_statement(p):
	"""
	command : statement
	"""
	return results
	
def p_statement_expr(p):
	"""
	statement : expr
			  | expr statement	
	"""
	return results


def p_expr_obj(p): #no modifier (reduct or extend)
	"""
	expr : MEMBER TIME 
		 | MEMBER
	     | ROLE PERMISSION
		 | CHANNEL INT
	"""
	res=None
	if p[1][1]=='member':
		if len(p)==2:
			res=(Mute(p[1][0]))
		else: 
			res=(Mute(p[1][0], p[2]))
	elif p[1][1]=='role':
		res=(Perm(p[1][0], p[2]))
	elif p[1][1]=='channel':
		res=Clear(p[1][0], p[2])
	elif p[1]=='rate':
		res=Rate(p[2])
	results.append(res)	
	return res
def p_extend_expr_obj(p):
	"""
	expr : EXTEND MEMBER 
	     | EXTEND ROLE
		 | EXTEND CHANNEL
	"""
	res=None
	if p[2][1]=='member':
		#res=(*p[2], 'ban')
		res=Ban(p[2][0])
	elif p[2][1]=='role':
		res=Delete(p[2][0])
	elif p[2][1]=='channel':
		res=Lock(p[2][0])
	elif p[2]=='rate':
		res=Percent(p[3])
	results.append(res)	
	return res

def p_reduct_expr_obj(p): 
	"""
	expr : REDUCT MEMBER 
	     | REDUCT ROLE COLOR
	"""
	res=None
	if p[2][1]=='member':
		res=(Rp(p[2][0]))
	elif p[2][1]=='role':
		res=Color(p[2][0],p[3])
	results.append(res)	
	return res
def p_error(p):
	if p:
		print("Syntax error at '%s'" % p)
		raise CommandSyntaxError(p.lineno, p.lexpos, p.value)
	else:
		print("Syntax error at EOF")
		raise CommandUnexpectedEOF()

"""lexer=lex.lex()
parser = yacc.yacc()"""
def parse(s):
	global results
	lexer=lex.lex()
	parser = yacc.yacc()
	yacc.parse(s)
	res= results
	results=[]
	print(res)
	return res
if __name__=='__main__':
	parse('<@#320394803> 12 +<@3209840324> <@32489238> 1d')

