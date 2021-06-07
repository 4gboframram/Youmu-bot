import os
import asyncio
import discord
from random import choice, choices
try: from discord_components import Button, ButtonStyle
except ImportError:
	os.system('pip install discord-components')
	from discord_components import Button, ButtonStyle

class Card:
	weights={
		'number': 10, 
		'skip': 3,
		'reverse': 3,
		'draw_2': 3,
		'wild': 2,
		'wild_draw_4': 1 
		}
	def __init__(self,*, color, card_type, value):
		self.color=color
		self.type=card_type
		self.value=value
	
	def new_random():

		card_types=[key for key in Card.weights]
		weights=(Card.weights[item] for item in Card.weights)
		card_type=choices(card_types,weights=weights)[0]
		color=None
		value=None

		if card_type in ['number', 'skip', 'reverse', 'draw_2']:
			color=choice(['yellow', 'green', 'red', 'blue'])

		if color and card_type=='number': 
			value=choice(range(10))
		return Card(color=color, card_type=card_type, value=value)

	def __repr__(self):
		return f"Card: Color={self.color}, Type={self.type}, Value={self.value}"
	
	def __str__(self):
		color=self.color if self.color else ''
		type_=self.type if self.type and not self.type=='number' else ''
		value=self.value if self.value or self.value==0 else ''
		return f"{color} {value}{type_.replace('_',' ')}".strip()
	
	def __xor__(self, other): #used for move validation
		return self.color==other.color or (self.value==other.value and self.type=='number') or self.type in ['wild', 'wild_draw_4'] or (self.type==other.type and self.type in ['reverse', 'skip', 'draw_2'])
	
	def __eq__(self, other):
		return self.type==other.type and self.value==other.value and self.color==other.color

class Player:
	def __init__(self, member: discord.Member):
		self.member=member
		self.hand=None
		self.selected_card=None
		self.mention=self.member.mention
		
	def __eq__(self, other):
		return self.member==other.member

	def __hash__(self):
		return hash(self.member.id)

class TurnEmbed(discord.Embed):
	def __init__(self, turn_owner: Player, current_card, player_hand, is_turn_owner=False):
		self.title=f'{turn_owner.member.name}\'s turn!'
		current_hand_str='\n\n'+'\n'.join([str(card) for card in player_hand]).title()
		if not is_turn_owner:
			self.description=f"Current card placed down:\n**{str(current_card).title()}**\n\nYour hand: {current_hand_str}"
		else: 
			self.description=f"Current card placed down:\n**{str(current_card).title()}\n*Press a button to place down that card. Only valid moves are shown*\n\n**Your hand: {current_hand_str}"
		self.color=0x53cc74
		super().__init__(title=self.title, description=self.description, color=self.color)
		self.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')

class UnoGame:
	def __init__(self, ctx, bot, *players):
		self.ctx=ctx
		self.bot=bot

		self.players=tuple(set([Player(player) for player in players]+[Player(self.ctx.author)]))
		self.is_running=False
		self.current_turn=0
		self.turn_owner=self.players[0]
		self.current_card=None
		self.turn_owner_message=None
		self.turn_in_progress=False
		self.invited_players=None
		self.invites=None

	async def invite(self):
		mentions=''
		for player in self.players:
			mentions+=player.mention+' '
		await self.ctx.send(f'Sending an invitation to all players via dm: {mentions}')

		self.invites=[]
		self.invited_players=set()
		#for player in self.players:
		await asyncio.gather(*map(self.deal_with_invites, self.players))

	async def deal_with_invites(self, player):
		embed=discord.Embed(title='✉️Invitation!✉️', description=f'{player.mention}, {self.ctx.author.mention} has challenged you (and perhaps others) to a game of **Uno**. \n\nPress the button within the next minute to start the game. \n\n*Remember that if you don\'t accept, you might lose a friend~*\n\nAccepted: {len(self.invited_players)} of {len(self.players)}', color=0x53cc74)
		embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
		button=Button(label='Accept Uno Invite', style=ButtonStyle.green, emoji='☑️')
		self.invites.append(await player.member.send(embed=embed, components=[button]))
		def check(res):
			return player.member.id == res.user.id

		try: 
				res = await self.bot.wait_for("button_click", check=check, timeout=60)
				if res.component.label=='Accept Uno Invite':
					await res.respond(type=6)
					
					if not player in self.invited_players:
						self.invited_players.add(Player(res.user))
						await player.member.send('Invited!')
						for invite in self.invites:
							embed=discord.Embed(title='✉️Invitation!✉️', description=f'{player.mention}, {self.ctx.author.mention} has challenged you (and perhaps others) to a game of **Uno**. \n\nPress the button within the next minute to start the game. \n\n*Remember that if you don\'t accept, you might lose a friend~*\n\nAccepted: {len(self.invited_players)} of {len(self.players)}', color=0x53cc74)
							embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
							await res.message.edit(embed=embed)
					
					if set(self.players)==self.invited_players:
						for invite in self.invites:
							try:
								await invite.delete()
							except: pass
						await self.start()

		except asyncio.TimeoutError:
				button=Button(label='Expired Invite :(', style=ButtonStyle.red, emoji='❎', disabled=True)
				for invite in self.invites:
					await invite.edit(components=[button])

	async def start(self):
		if not self.is_running:
			self.is_running=True
			def get_starting_card(): #reset until card has any color (not wild)
				card=Card.new_random()
				if card.color:
					self.current_card=card
				else: get_starting_card()
			get_starting_card()
			for player in self.players:
				player.hand=[Card.new_random() for i in range(7)]
				await player.member.send('Uno Game Started')
			while self.is_running:
				await self.take_turn()
				
			print('success')
			return
	
	async def take_turn(self):
		valid_cards=[card for card in self.turn_owner.hand if card^self.current_card]

		print('Valid moves:', [str(card) for card in valid_cards])

		valid_move_buttons=[Button(label=str(card).title(), style=ButtonStyle.gray) for card in valid_cards]
		valid_move_buttons=[valid_move_buttons[i:i + 5] for i in range(0, len(valid_move_buttons), 5)]
		for player in self.players:
			if player==self.turn_owner:
				components=valid_move_buttons if valid_move_buttons else []
				self.turn_owner_message=await player.member.send(embed=TurnEmbed(self.turn_owner, self.current_card, player.hand), components=components)

			else: await player.member.send(embed=TurnEmbed(self.turn_owner, self.current_card, player.hand))

		if not valid_cards:
					self.turn_owner.hand.append(Card.new_random())
					self.current_turn+=1
					
					for player in self.players:
						await player.member.send(f'{self.turn_owner.member.name} had no cards to play and had to pick up a card. {self.players[(self.current_turn+1)% len(self.players)].member.name}\'s turn is next.')

					self.turn_owner=self.players[self.current_turn % len(self.players)]
					return
		def check(res):
			return self.turn_owner.member == res.user and res.message==self.turn_owner_message

		try:
			res = await self.bot.wait_for("button_click", check=check, timeout=60)

			await res.respond(type=6)

			card=[card for card in self.turn_owner.hand if str(card).title()==res.component.label][0]
			self.turn_owner.hand.remove(card)
			
			if not self.turn_owner.hand:
				for player in self.players:
					embed=discord.Embed(title='Game Over!', description=f'{player.mention}, {self.turn_owner.name} has won the game', color=0x53cc74)
					embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
					await player.member.send(embed=embed)
					self.is_running=False
					return
			print(card)
			print([str(card) for card in self.turn_owner.hand])

			if card.type=='wild':
				buttons=[[Button(label='Green', style=ButtonStyle.green), Button(label='Red', style=ButtonStyle.red), Button(label='Blue', style=ButtonStyle.blue), Button(label='Yellow', style=ButtonStyle.gray)]]

				embed=discord.Embed(title='Wild!', description=f'Choose the color you would like to use for your wild below. :3', color=0x53cc74)
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			
				wild_prompt=await self.turn_owner.member.send(embed=embed, components=buttons)
				def check(res):
					return self.turn_owner.member.id == res.user.id and res.message==wild_prompt
				try: 
					res = await self.bot.wait_for("button_click", check=check, timeout=60)
					label=res.component.label
					
					if label=='Green': card.color='green'
					elif label=='Red': card.color='red'
					elif label=='Blue': card.color='blue'
					else: card.color='yellow'

				except asyncio.TimeoutError:
					card.color=choice(['red', 'green', 'blue', 'yellow'])
				

			elif card.type=='reverse':
				list_of_players=list(self.players)
				list_of_players.reverse()
				self.players=tuple(list_of_players)
				self.current_turn=-self.current_turn
				
			elif card.type=='draw_2':
				self.players[(self.current_turn+1) % len(self.players)].hand.append(Card.new_random())
				self.players[(self.current_turn+1) % len(self.players)].hand.append(Card.new_random())
				self.current_turn+=1				

			elif card.type=='skip':
				self.current_turn+=1

			elif card.type=='wild_draw_4':
				buttons=[Button(label='Green', style=ButtonStyle.green), Button(label='Red', style=ButtonStyle.red), Button(label='Blue', style=ButtonStyle.blue), Button(label='Yellow', style=ButtonStyle.gray)]

				embed=discord.Embed(title='Wild (But The Next Person Will Hate You)!', description=f'Choose the color you would like to use for your wild below. :3', color=0x53cc74)
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			
				wild_prompt=await self.turn_owner.member.send(embed=embed, components=[buttons])
				def check(res):
					return self.turn_owner.member.id == res.user.id and res.message==wild_prompt
				try: 
					res = await self.bot.wait_for("button_click", check=check, timeout=60)
					label=res.component.label
					
					if label=='Green': card.color='green'
					elif label=='Red': card.color='red'
					elif label=='Blue': card.color='blue'
					else: card.color='yellow'

				except asyncio.TimeoutError:
					card.color=choice(['red', 'green', 'blue', 'yellow'])
				finally: 
					self.players[(self.current_turn+1) % len(self.players)].hand.append(Card.new_random())
					self.players[(self.current_turn+1) % len(self.players)].hand.append(Card.new_random())
					self.players[(self.current_turn+1) % len(self.players)].hand.append(Card.new_random())
					self.players[(self.current_turn+1) % len(self.players)].hand.append(Card.new_random())
					self.current_turn+=1

			self.current_card=card
			await res.respond(type=6)
			for player in self.players:
				await player.member.send(f'{self.turn_owner.member.name} played a **{str(card).title()}**. {self.players[(self.current_turn+1) % len(self.players)].member.name}\'s turn is next.')
			self.current_turn+=1
			self.turn_owner=self.players[self.current_turn % len(self.players)]
			print('turn end')
			await self.turn_owner_message.edit(components=[])
			return
		except asyncio.TimeoutError:
			for player in self.players:
				await player.member.send(f'Game over because I don\'t have time to wait for {self.turn_owner.member.name} to finish and I need to cook Yuyuko-sama\'s dinner')
			self.is_running=False
			return

if __name__=='__main__':
	print('Printing random cards...')
	for i in range(15):
		print(Card.new_random())