import os
import asyncio
import discord
from typing import Union
try: from discord_components import Button, ButtonStyle
except ImportError:
	os.system('pip install discord-components')
	from discord_components import Button, ButtonStyle

class Tile: 
	def __init__(self, owner:Union[discord.Member, None]=None):
		self.owner=owner

	def __repr__(self):
		if self.owner==None:
			return 'empty'
		return self.owner.name
	def __eq__(self, other):
		return self.owner==other.owner

class TTTGame:
	def __init__(self, bot, ctx, players: tuple):
		self.bot=bot
		self.channel=None
		self.ctx=ctx

		self.players=players
		self.players_dynamic=list(self.players) #used for turn order to swap the players
		self.state=[Tile()]*9

		self.buttons=[Button(emoji='⬛', id=i+1) for i in range(9)] #id zero tends to be wonky
		self.buttons_inline=None #it's annoying to work with a multidimensional matrix 
		#so we have a flat version and a the version that will be used on the bot
		self.turn_owner=self.players[0]
		self.message=None

	def update_inline_buttons(self):
		self.buttons_inline=[self.buttons[i:i + 3] for i in range(0, len(self.buttons), 3)]

	async def start(self):
		self.update_inline_buttons()
		self.message=await self.ctx.send(content=f'Game has started, {self.players[0].mention}, your turn first', components=self.buttons_inline)
		await self.take_turn(self.turn_owner)

	def check_win(self):
		state=self.state
		
		winning_combos=[[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
		player_1_owned=[i for i in range(9) if self.state[i].owner==self.players[0]]
		player_2_owned=[i for i in range(9) if self.state[i].owner==self.players[1]]
		for combo in winning_combos:
			if set(combo).issubset(set(player_1_owned)) or set(combo).issubset(set(player_2_owned)):
				return True
		if all([tile.owner for tile in state]): #check for full board
			return None
		return False
	async def take_turn(self, player):
		def check(res):
			return res.user.id == player.id and res.channel == self.ctx.channel and res.component.label == None

		try:
			res = await self.bot.wait_for("button_click", check=check, timeout=600)

			button_pos=int(res.component.id)

			await res.respond(type=6)
			player_=res.user
			await self.process_turn(player_, button_pos-1)
		except asyncio.TimeoutError:
			await self.ctx.send("Game ends in a draw because you were taking too long. I have to go cook dinner for Yuyuko-sama now")
			self.buttons=[Button(id=button.id, emoji=button.emoji, style=button.style, disabled=True) for button in self.buttons]
			self.update_inline_buttons()
			await self.message.edit(components=self.buttons_inline)

	async def process_turn(self, player: discord.Member, position: int): 

		self.state[position]=Tile(player)
		if player==self.players[0]:
			self.buttons[position]=Button(style=ButtonStyle.blue, emoji='⬛', id=self.buttons[position].id, disabled=True)
		else:
			self.buttons[position]=Button(style=ButtonStyle.red, emoji='⬛', id=self.buttons[position].id, disabled=True)
		self.update_inline_buttons()
		await self.message.edit(components=self.buttons_inline)


		win=self.check_win()
		if win:
			embed=discord.Embed(title='Winner!', description=f'{player.mention}, you win this game of **Tic Tac Toe**', color=0x53cc74)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			
			self.buttons=[Button(id=button.id, emoji=button.emoji, style=button.style, disabled=True) for button in self.buttons]
			self.update_inline_buttons()
			await self.message.edit(content='Game Over', embed=embed, components=self.buttons_inline)
			return
		if win==None:
			embed=discord.Embed(title='Draw', description=f'Nobody wins this game of **Tic Tac Toe**', color=0x53cc74)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			
			self.buttons=[Button(id=button.id, emoji=button.emoji, style=button.style, disabled=True) for button in self.buttons]
			self.update_inline_buttons()
			await self.message.edit(content='Game Over!', embed=embed, components=self.buttons_inline)
			return
		self.players_dynamic.reverse()
		self.turn_owner=self.players_dynamic[0]

		await self.message.edit(content=f'{self.turn_owner.mention}, your turn')

		await self.take_turn(self.turn_owner)