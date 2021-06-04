import os
from keep_alive import keep_alive
from parser import parse, CommandSyntaxError, CommandUnexpectedEOF
import asyncio
from random import choice
import requests
import actions
from leveling import LevelDB
from requests.exceptions import RequestException
import tictactoe
try:
	import discord
	from discord.ext import commands
except ImportError: 
	os.system('pip install discord')
	import discord
	from discord.ext import commands

try: from discord_slash import SlashCommand, SlashContext
except ImportError:
	os.system('pip install discord-py-slash-command')
	from discord_slash import SlashCommand, SlashContext

try: from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
except ImportError:
	os.system('pip install discord-components')
	from discord_components import DiscordComponents, Button, ButtonStyle

bot = commands.Bot(command_prefix=";",help_command=None,)
slash = SlashCommand(bot, sync_commands=False) #remember to change back to true
spamlogger={}

ping_messages=[
'There\'s nothing my Roukanken can\'t cut!',
"Everyone talks about my sword Roukanken, but not my other sword Hakurouken. *sad Hakurouken noises* ", 
"Everyone always says 'Youmu best girl', but not 'How is best girl?' :(", 
"Me or Reimu? That's like asking 'would you rather a brown-haired broke girl or a sweet wife.'", 
'Dammit Yuyuko-sama. The fridge is empty again.', 
'If it taste bad I can always shove this up your ass~', 
'I cut the heavens. I cut reason. I even cut time itself.', 
'The things that cannot be cut by my Roukanken, forged by youkai, are close to none!', 
"Well I don't know how it look but for some reason I want a sperm emoji... like this I can say \"Hey look... it's Myon!\"", 
"Error 404: Ping message not found.", 
"I am half-human half-sperm. I mean ghost! Dammit perverts!"
]

presences=[
'Gardening at the Hakugyokurou', 
"Cooking Yuyuko-sama's dinner", 
"Filling up the fridge for Yuyuko-sama", 
"Myon uwu", 
"Eating watermelon with Yuyuko-sama",
"Myon?",
"Being best girl",
"Needing some sleep",
"Wanting headpats"
]
db=LevelDB('Levels')
guild_ids=[]
presence_is_looping=False
spamlogger_is_clearing=False
last_presence=None
comp=DiscordComponents(bot)

############
#on_ready and background tasks
############

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected')
	global guild_ids
	guild_ids=[guild.id for guild in bot.guilds]
	await asyncio.gather(hourly_precenses(), clear_spamlogger())
	

async def hourly_precenses():
	global presence_is_looping
	if not presence_is_looping: #prevent from looping multiple times If on_ready() is called multiple times
		presence_is_looping=True
		while True:

			presence=choice(presences)
			global last_presence
			if presence==last_presence: #prevent the same status from appearing twice in a row
				continue
			last_presence=presence

			print("changing presence...")
			"""await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=presence, url='https://www.youtube.com/watch?v=FtutLA63Cp8'))"""
			await bot.change_presence(activity=discord.Game(name=presence))
			print("done...") 
			await asyncio.sleep(3600)

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	#print(message.content)
	global db
	guild_id=message.guild.id
	member_id=message.author.id

	try: spamlogger[member_id]+=1
	except KeyError: 
		spamlogger[member_id]=1
	try: await db.add_xp(guild_id, member_id, 2*1/(spamlogger[member_id]+1), on_level_up, message)
	except: 
		if not 'g'+str(guild_id) in db.list_of_tables():
			db.add_guild(guild_id)
		db.add_member(guild_id, member_id)
		await db.add_xp(guild_id, member_id, 2*1/(spamlogger[member_id]+1), on_level_up, message)
	await bot.process_commands(message)

async def clear_spamlogger():
	global spamlogger_is_clearing
	global spamlogger
	if not spamlogger_is_clearing:
		while True:
			spamlogger_is_clearing=True
			spamlogger={}
			await asyncio.sleep(60)

async def on_level_up(message):
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

@bot.event
async def on_guild_channel_create(channel):
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

@bot.event
async def on_guild_join(guild):
	global guild_ids
	guild_ids.append(guild.id)

##########
#Commands
##########

@bot.command()
async def ping(ctx):
	await ctx.send(f'{choice(ping_messages)} ({round(bot.latency*1000, 2)}ms)')

@bot.command()
async def cut(ctx, *, args):
	try:
		results=parse(args)
	except Exception as e: 
		if isinstance(e, CommandSyntaxError) or isinstance(e, CommandUnexpectedEOF):
			await ctx.send(e.message)
			return
		else: raise e
	coroutines=[result.run(ctx) for result in results]
	await asyncio.gather(*coroutines)

@bot.command()
async def rate(ctx, *, thing):
	h=hash(thing)%11
	embed=discord.Embed(title='Rate',description=f"I would rate *{thing}* a {h} out of 10",colour=0xcc00ff)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)

@bot.command()
async def percent(ctx, *, thing):
	h=hash(str(ctx.author.id)+f' {thing}')%101
	embed=discord.Embed(title='Rate',description=f"{ctx.author.mention}, you are {h}% {thing}",colour=0xcc00ff)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)

@bot.command()
async def ttt(ctx, player: discord.Member):
	embed=discord.Embed(title='✉️Invitation!✉️', description=f'{player.mention}, {ctx.author.mention} has challenged you to a game of **Tic Tac Toe**. \n\nPress the button within the next minute to start the game. \n\n*Remember that if you don\'t accept, you might lose a friend~*', color=0x53cc74)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	button=Button(label='Accept Tic Tac Toe Invite', style=ButtonStyle.green, emoji='☑️')
	m=await ctx.send(embed=embed, components=[button])
	def check(res):
		return player.id == res.user.id and res.channel == ctx.channel
	try: 
		res = await bot.wait_for("button_click", check=check, timeout=60)
		if res.component.label=='Accept Tic Tac Toe Invite':
			game=tictactoe.TTTGame(bot, ctx, (ctx.author, player))
			await m.delete()
			await game.start()
	except asyncio.TimeoutError:
		button=Button(label='Expired Invite :(', style=ButtonStyle.red, emoji='❎', disabled=True)
		await m.edit(components=[button])
		

@bot.command()
async def inspire(ctx):
	try:
		url = 'http://inspirobot.me/api?generate=true'
		params = {'generate': 'true'}
		response = requests.get(url, params, timeout=10)
		image = response.text
		embed=discord.Embed(title='Inspiration', colour=0x53cc74)
		embed.set_image(url=image)
		embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
		await ctx.send(embed=embed)

	except RequestException:

		await ctx.send('Inspirobot is broken, there is no reason to live.')

@bot.command()
async def help(ctx):
	embed=discord.Embed(title='Help',description=f"Check out the documentation that contains the help here:", color=0x53cc74)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed, components=[Button(style=ButtonStyle.URL, label="Github", url="https://github.com/4gboframram/Youmu-bot-")])

########
#Slash Commands
########

@slash.slash(name="cut", description='Cuts a variety of things', guild_ids=guild_ids)
async def _cut(ctx, *, args):
	try:
		results=parse(args)
	except Exception as e: 
		if isinstance(e, CommandSyntaxError) or isinstance(e, CommandUnexpectedEOF):
			await ctx.send(e.message)
			return
		else: raise e
	def check_slash(result):
		if isinstance(result, actions.Clear):
			return result.run_slash(ctx)
		return result.run(ctx)
	coroutines=[check_slash(result) for result in results]
	await asyncio.gather(*coroutines)


@slash.slash(name="help", description='Go to the github documentation for help about this bot\'s commands', guild_ids=guild_ids)
async def _help(ctx):
	embed=discord.Embed(title='Help',description=f"Check out the documentation that contains the help here: https://github.com/4gboframram/Youmu-bot-", color=0x53cc74)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)
	

@slash.slash(name="rate", description='What would I rate [thing] out of 10?', guild_ids=guild_ids)
async def _rate(ctx, *, thing):
	h=hash(thing)%11
	embed=discord.Embed(title='Rate',description=f"I would rate *{thing}* a {h} out of 10",colour=0xcc00ff)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)

@slash.slash(name="ping", description='Pong?', guild_ids=guild_ids)
async def _ping(ctx: SlashContext):
	await ctx.send(f'{choice(ping_messages)} ({round(bot.latency*1000, 2)}ms)')

@slash.slash(name="inspire", description='Inspiration anyone? (Generated using Inspirobot)', guild_ids=guild_ids)
async def _inspire(ctx):

	try:
		url = 'http://inspirobot.me/api?generate=true'
		params = {'generate': 'true'}
		response = requests.get(url, params, timeout=10)
		image = response.text
		embed=discord.Embed(title='Inspiration', colour=0x53cc74)
		embed.set_image(url=image)
		embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
		await ctx.send(embed=embed)

	except RequestException:

		await ctx.send('Inspirobot is broken, there is no reason to live.')

##################
#Leveing Commands
#################
@bot.command()
async def xp(ctx):
	stats=db.get_member_stats(ctx.guild.id, ctx.author.id)
	embed=discord.Embed(title='Level Up!',description=f"{ctx.author.mention}, you have leveled are level {stats[1]}, and {db.rule(stats[1]+1)-stats[2]} xp from leveling up to {stats[1]+1}", color=0x53cc74)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)

@bot.command()
async def rank(ctx):
	embed=discord.Embed(title='Rank?',description=f"{ctx.author.mention}, you are rank {db.get_member_rank(ctx.guild.id, ctx.author.id)} in the server!", color=0x53cc74)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)

keep_alive()
bot.run(os.getenv('TOKEN'))