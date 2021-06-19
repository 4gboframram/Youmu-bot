import os
import discord
import asyncio 
from random import choice
from discord_components import DiscordComponents, Button, ButtonStyle

async def presence_hourly(bot, presences, last_presence, presence_is_looping):
	if not presence_is_looping: #prevent from looping multiple times If on_ready() is called multiple times
		presence_is_looping=True
		while True:

			presence=choice(presences)
			if presence==last_presence: #prevent the same status from appearing twice in a row
				continue
			last_presence=presence

			print("changing presence...")
			"""await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=presence, url='https://www.youtube.com/watch?v=FtutLA63Cp8'))"""
			await bot.change_presence(activity=discord.Game(name=presence))
			print("done...") 
			await asyncio.sleep(3600)

async def clear_spamlogger(spamlogger_is_clearing, spamlogger):
	
	if not spamlogger_is_clearing:
		while True:
			spamlogger_is_clearing=True
			spamlogger={}
			await asyncio.sleep(60)

async def process_levels(bot, message, spamlogger, db):
	if message.author.bot:
		return
	#print(message.content)
	guild_id=message.guild.id
	member_id=message.author.id

	try: spamlogger[member_id]+=1
	except KeyError: 
		spamlogger[member_id]=1
	try: await db.add_xp(guild_id, member_id, 2*1/(spamlogger[member_id]+1), on_level_up, bot,  message, db)
	except: 
		if not 'g'+str(guild_id) in db.list_of_tables():
			db.add_guild(guild_id)
		db.add_member(guild_id, member_id)
		await db.add_xp(guild_id, member_id, 2*1/(spamlogger[member_id]+1), on_level_up, bot, message, db)
	await bot.process_commands(message)

async def on_level_up(bot, message, db):
	embed=discord.Embed(title='Level Up!',description=f"{message.author.mention}, you have leveled up to level {db.get_member_stats(message.guild.id, message.author.id)[1]}!", color=0x53cc74)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	try:
		m=await message.channel.send(embed=embed,components=[Button(style=ButtonStyle.red, label="Close", emoji=bot.get_emoji(844701344719962132)),])
	except: 
		m=await message.channel.send(embed=embed,components=[Button(style=ButtonStyle.red, label="Close", emoji='⚔️'),],)

	def check(res):
		return message.author == res.user and res.channel == message.channel 

	try:
		res = await bot.wait_for("button_click", check=check, timeout=60)
		if res.component.label=='Close':
			await m.delete()
	except asyncio.TimeoutError:
		await m.edit(components=[Button(style=ButtonStyle.red, label="Close", emoji=bot.get_emoji(844701344719962132), disabled=True),]) 
		pass

async def update_muted_role(channel):
	print('updating muted role channel perms...')
	guild=channel.guild
	role = discord.utils.get(guild.roles, name="Speaking Cut")
	if not role:
			print('creaing role...')
			role=await guild.create_role(name="Speaking Cut")
			permissions = discord.Permissions()
			permissions.update(send_messages = False)

			await role.edit(reason = None, colour = discord.Colour.black(), permissions=permissions)
			print('Changing perms')
			for channel in guild.channels:
				await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
	else: await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
	print('success!')