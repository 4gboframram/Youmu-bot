import discord
import asyncio
from PIL import Image
import random
import io
import os

class NoMemberPerms(Exception): #Just used for an if statement
	pass

###############
#Member
###############
class Ban: #Extend 

	def __init__(self, user_id):
		self.user_id=user_id

	async def run(self, ctx):
		print(self.user_id)
		member=await ctx.guild.fetch_member(self.user_id)
		reason='You broke the rules.'
		member_perms=member.guild_permissions
		if ctx.author.guild_permissions.ban_members:
			print('can ban')
			if any([member_perms.manage_messages, member_perms.kick_members, member_perms.ban_members, member_perms.manage_guild]):
				embed = discord.Embed(title="Oops",description="You do not have the permission to cut that user out of this server permanently through commands", colour=0xff0000)
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
				await ctx.send(embed=embed)
			else:
				try:
					await member.ban(reason=reason)
					await ctx.send(f'{member.mention} has been cut out of the server permanently.')
				except discord.errors.Forbidden: 
					await ctx.send('I do not have the permissions to cut that user\'s ability to speak permanently. Try moving my role above theirs and making sure I can ban users')
		else: 
			embed = discord.Embed(title="Oops",description="You do not have the permission to cut that user out of this server permanently", colour=0xff0000)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			await ctx.send(embed=embed)

class Mute: #No operators
	def __init__(self, user_id: int, t:int = None):
		self.t=t
		self.user_id=user_id
		#self.bot=None
		
	async def run(self, ctx):
		role = discord.utils.get(ctx.guild.roles, name="Speaking Cut")
		if not role:
			role=await ctx.guild.create_role(name="Speaking Cut")
			permissions = discord.Permissions()
			permissions.update(send_messages = False)

			await role.edit(reason = None, colour = discord.Colour.black(), permissions=permissions)

		member=await ctx.guild.fetch_member(self.user_id)
		member_perms=member.guild_permissions

		if ctx.author.guild_permissions.manage_messages and not any([member_perms.manage_messages, member_perms.kick_members, member_perms.ban_members, member_perms.manage_guild]):
			try:
				await member.add_roles(role)
			except discord.errors.Forbidden:
				await ctx.send('I cannot add roles to that user. Try checking my permissions')
				return
			if self.t:
				embed = discord.Embed(title="Cut!",
					description=f"{member.mention} has their ability to speak cut for {self.t} seconds",
					colour=0xfff200)
			
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
				await ctx.send(embed=embed)
				await asyncio.sleep(self.t)
				await member.remove_roles(role)
				embed = discord.Embed(title="Uncut!",
					description=f"{member.mention}'s ability to speak has been uncut",
					colour=0xfff200)
			
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
				await ctx.send(embed=embed)
			else: 
				
				if role in member.roles:
					await member.remove_roles(role)
					embed = discord.Embed(title="Uncut!",
					description=f"{member.mention}'s ability to speak has been uncut",
					colour=0xfff200)
			
					embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
					await ctx.send(embed=embed)
				else: 
					await member.add_roles(role)
					embed = discord.Embed(title="Cut!",
					description=f"{member.mention} has their ability to speak cut indefinitely.",
					colour=0xfff200)
			
					embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
					await ctx.send(embed=embed)
					await member.send(f'Your ability to speak in {ctx.guild.name} has been cut indefinitely. Don\'t leave yet. You\'ll probably have it uncut soon')
		else: 
			embed = discord.Embed(title="Oops",description="You do not have the permission to cut that user's ability to speak", colour=0xff0000)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			await ctx.send(embed=embed)


class Rp: #Reduce
	def __init__(self, user_id):
		self.user_id=user_id
	
	async def run(self, ctx):
		member = await ctx.guild.fetch_member(self.user_id)
		filename = random.choice(["cut.gif", "cut2.gif", "cut3.gif"])
		path = os.path.join("assets", filename)
		embed = discord.Embed(title="Cut!", description=f'{ctx.author.mention} slices {member.mention} in half', color=0x53cc74) 
		embed.set_image(url=f"attachment://cut.gif")
		file = discord.File(path, filename="cut.gif")
		embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
		await ctx.send(embed=embed, file=file)

#################
#Role
#################
class Delete: #extend
	def __init__(self, role_id):
		self.role_id=role_id

	async def run(self, ctx):
		role=ctx.guild.get_role(self.role_id)
		author_highest_pos=ctx.author.roles[-1].position

		if ctx.author.guild_permissions.manage_roles and author_highest_pos>role.position:
			
			await role.delete()
			embed = discord.Embed(title="Cut!",
				description=f"Role has been successfully cut out of existence",
				colour=0xfff200
				)
			
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			await ctx.send(embed=embed)
		
	
class Perm: #No operator
	def __init__(self, role_id, perm):
		self.role_id=role_id
		self.perm=perm
	async def run(self, ctx):
		perm=self.perm
		role=ctx.guild.get_role(self.role_id)
		permissions=discord.Permissions()
		state=None
		author_highest_pos=ctx.author.roles[-1].position
		try:
			if author_highest_pos<role.position:
				raise NoMemberPerms
			if perm=='add_reactions':
				if ctx.author.guild_permissions.manage_roles:
					state=not role.permissions.add_reactions
					permissions.update(add_reactions=state)
			elif perm=='kick_members':
				if ctx.author.guild_permissions.manage_guild:
					state=not role.permissions.kick_members
					permissions.update(kick_members=state)
			elif perm=='ban_members':
				if ctx.author.guild_permissions.manage_guild:
					state=not role.permissions.ban_members
					permissions.update(ban_members=state)	
				else: raise NoMemberPerms
			elif perm=='external_emojis':
				if ctx.author.guild_permissions.manage_guild:
					state=not role.permissions.external_emojis
					permissions.update(external_emojis=state)	
				else: raise NoMemberPerms
			elif perm=='manage_emojis':
				if ctx.author.guild_permissions.manage_roles:
					state=not role.permissions.manage_emojis
					permissions.update(manage_emojis=state)	
				else: raise NoMemberPerms
			elif perm=='change_nickname':
				if ctx.author.guild_permissions.manage_roles:
					state=not role.permissions.change_nickname
					permissions.update(change_nickname=state)	
				else: raise NoMemberPerms
			elif perm=='manage_nicknames':
				if ctx.author.guild_permissions.manage_roles:
					state=not role.permissions.change_nickname
					permissions.update(manage_nicknames=state)	
				else: raise NoMemberPerms
			elif perm=='mention_everyone':
				if ctx.author.guild_permissions.manage_roles:
					state=not role.permissions.mention_everyone
					permissions.update(mention_everyone=state)	
				else: raise NoMemberPerms
			
			else: 
				embed = discord.Embed(title="Oops",description=f"Invalid permission, {perm}. I can't change every single type of permission because some are not used that frequently or because I think there should be more thought into assigning that permission to someone.", colour=0xff0000)
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
				await ctx.send(embed=embed)
		except NoMemberPerms: 
			embed = discord.Embed(title="Oops",description=f"You do not have the permission to cut the permission *{perm}* of that role", colour=0xff0000)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			await ctx.send(embed=embed)
			return

		try:
			await role.edit(permissions=permissions)
			await ctx.send(f'Successfully cut *{perm}* for {role.mention} to *{state}*')
		except discord.errors.Forbidden:
			await ctx.send("I do not have permissions to edit that role. Make sure that I have permissions to edit roles, and my role is above that role.")

class Color: #Minus
	def __init__(self, role_id, value):
		self.role_id=role_id
		self.value=value

	async def run(self, ctx):
		role=ctx.guild.get_role(self.role_id)
		author_highest_pos=ctx.author.roles[-1].position
		if (ctx.author.guild_permissions.manage_roles and author_highest_pos>role.position) or ctx.author.id==ctx.guild.owner_id:
			try:
				await role.edit(reason='invoked with ;cut command', colour=self.value)
				color = f"#{self.value:06X}"
				img = Image.new('RGB', (100, 100), color)
				file = io.BytesIO()
				img.save(file, format="png", optimize=True, compress_level=9)
				file.seek(0)
				await ctx.send(f'{role.mention} has had their color cut to {color}', file=discord.File(file, "color.png"))
			except discord.errors.Forbidden: 
				await ctx.send("I do not have permissions to edit that role. Make sure that I have permissions to edit roles, and my role is above that role.")
		else: 
				embed = discord.Embed(title="Oops",description=f"You do not have the permission to cut that role's color", colour=0xff0000)
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
				await ctx.send(embed=embed)
    
    
#############
#Channels
#############

class Lock:
	def __init__(self, channel_id):
		self.channel_id=channel_id

	def cut_message(state: bool)->str:
		if state:
			return "Uncut!"
		return "Cut!"

	async def run(self, ctx):
		channel=ctx.guild.get_channel(self.channel_id)
		state=not ctx.channel.overwrites_for(ctx.guild.default_role).send_messages
		print(state)
		if ctx.author.guild_permissions.manage_channels:
			try:
				await channel.set_permissions(ctx.guild.default_role, send_messages=state)
				embed = discord.Embed(title=Lock.cut_message(state),description=f"Channel, {channel.mention} has had their ability to speak {Lock.cut_message(state).lower().strip('!')} until someone {Lock.cut_message(not state).lower().strip('!')+'s'} it", colour=0x1fdca7)
				embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
				await ctx.send(embed=embed)
			except discord.errors.Forbidden:
				await ctx.send("I do not have permissions to edit that channel. Make sure that I have permissions to edit channels.")
		else: 
			embed = discord.Embed(title="Oops",description=f"You do not have the permission to cut messages out of channels", colour=0xff0000)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			await ctx.send(embed=embed)

class Clear:
	def __init__(self, channel_id, count):
		self.channel_id=channel_id
		self.count=count
	
	async def run(self, ctx):
		channel=ctx.guild.get_channel(self.channel_id)
		try:
			await channel.purge(limit=self.count+1)
			embed=discord.Embed(title="Cut!", description=f'Cut {self.count} messages from {channel.mention}', color=0xfd6d98)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			
			
			bot_message=await ctx.send(embed=embed)
			await asyncio.sleep(10)
			await bot_message.delete()
		except discord.errors.Forbidden:
			await ctx.send("I do not have permissions to delete messages. Make sure that I have the permission to manage messages.")
	async def run_slash(self, ctx):
		channel=ctx.guild.get_channel(self.channel_id)
		try:
			await channel.purge(limit=self.count)
			embed=discord.Embed(title="Cut!", description=f'Cut {self.count} messages from {channel.mention}', color=0xfd6d98)
			embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
			
			
			bot_message=await ctx.send(embed=embed)
			await asyncio.sleep(10)
			await bot_message.delete()
		except discord.errors.Forbidden:
			await ctx.send("I do not have permissions to delete messages. Make sure that I have the permission to manage messages.")

###########
#Rate
###########

class Rate:
	def __init__(self, thing):
		self.thing=thing
	
	async def run(self, ctx):
		h=hash(str(ctx.author.id)+f' {self.thing}')%11
		embed=discord.Embed(title='Rate',description=f"I would rate *{self.thing}* a {h} out of 10",colour=0xcc00ff)
		embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
		await ctx.send(embed=embed)

class Percent:
	def __init__(self, thing):
		self.thing=thing
	
	async def run(self, ctx):
		h=hash(str(ctx.author.id)+f' {self.thing}')%101
		embed=discord.Embed(title='Rate', description=f"{ctx.author.mention}, you are {h}% *{self.thing}*",colour=0xcc00ff)
		embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
		await ctx.send(embed=embed)
