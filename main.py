###################
#Bot Created by #RamRam#0001 on discord
#Bugfixing and optimization
#by PervyStella#5667 on discord
###################
import os
from keep_alive import keep_alive
from parser import parse, CommandSyntaxError, CommandUnexpectedEOF
import asyncio
from random import choice, randint
import requests
import actions
import db
from requests.exceptions import RequestException
import sqlite3
import tictactoe
import uno
import error_handling
from constants import Constants, YoumuEmbed
import sauces
import sys
import discord
from discord.ext import commands
from skingrabber import skingrabber
from discord_slash import SlashCommand, SlashContext
from discord_components import DiscordComponents, Button, ButtonStyle
import argparse
import pathlib
import aiosqlite

TOKEN = os.getenv('TOKEN')

if TOKEN is None:
	raise ValueError("Please set your discord bot token to the TOKEN enviroment variable")

parser = argparse.ArgumentParser(description="Youmu bot, a wip Discord bot with many functionalities.")
listen_group = parser.add_mutually_exclusive_group()
listen_group.add_argument("--unix", nargs=1, type=pathlib.Path, metavar="path", help="Create a status web server listening in a unix socket")
tcp_group = listen_group.add_argument_group("--tcp")
listen_group.add_argument("--tcp", nargs=2, type=str, metavar=("address", "port"), help="Create a status web server listening in a tcp socket")
args = parser.parse_args()

levels_tbl: db.LevelsTable = None
bot_channel_tbl: db.BotChannelsTable = None
xp_channel_tbl: db.ExpChannelsTable = None
prefix_tbl: db.PrefixTable = None

async def get_prefix(bot, message):
	guild_prefixes = await prefix_tbl.get_prefixes(message.guild.id)
	return commands.when_mentioned_or(*guild_prefixes)(bot, message)

bot = commands.Bot(command_prefix=get_prefix, help_command=None)
slash = SlashCommand(bot, sync_commands=False) #remember to change back to true
spamlogger={}
comp=DiscordComponents(bot)

ping_messages=Constants.ping_messages
presences=Constants.presences

guild_ids=[]
presence_is_looping=False
spamlogger_is_clearing=False
last_presence=None


async def is_botchannel(ctx):
	return await bot_channel_tbl.contains_channel(ctx.channel.id)

############
# on_ready and background tasks
############

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected')
	
	if args.unix:
		address = args.unix[0]
	elif args.tcp:
		address = tuple(args.tcp)
	else:
		address = None
	if address is not None:
		asyncio.create_task(keep_alive(address), name="status server")
		print("Status server is starting")
	#print([guild for guild in bot.guilds])
	global guild_ids
	guild_ids=[guild.id for guild in bot.guilds]
	await asyncio.gather(hourly_precenses(), clear_spamlogger())

async def hourly_precenses():
	global presence_is_looping
	if not presence_is_looping: #prevent from looping multiple times if on_ready() is called multiple times
		presence_is_looping=True
		while True:
			presence=choice(presences)
			global last_presence
			if presence==last_presence: #prevent the same status from appearing twice in a row
				continue
			last_presence=presence

			print("changing presence...")
			await bot.change_presence(activity=discord.Game(name=presence))
			print("done...") 
			await asyncio.sleep(3600)

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	
	await bot.process_commands(message) 

	if isinstance(message.channel, 	discord.channel.DMChannel):
		return

	guild_id = message.guild.id
	member_id = message.author.id

	if await xp_channel_tbl.contains_channel(message.channel.id):
		try:
			spamlogger[member_id] += 1
		except KeyError: 
			spamlogger[member_id] = 1

		old_level, new_level = await levels_tbl.add_exp(guild_id, member_id, 2 * 1 / (spamlogger[member_id] + 1))
		if old_level != new_level:
			await on_level_up(message)
	
async def clear_spamlogger():
	global spamlogger_is_clearing
	global spamlogger
	if not spamlogger_is_clearing:
		while True:
			spamlogger_is_clearing=True
			spamlogger={}
			await asyncio.sleep(60)

async def on_level_up(message):
	stats = await levels_tbl.get_member_stats(message.guild.id, message.author.id)
	embed = YoumuEmbed(title='Level Up!',description=f"{message.author.mention}, you have leveled up to level {stats.level}!", color=0x53cc74)
	try:
		m = await message.channel.send(embed=embed, components=[Button(style=ButtonStyle.red, label="Close", emoji=bot.get_emoji(844701344719962132)),])
	except Exception: 
		m = await message.channel.send(embed=embed, components=[Button(style=ButtonStyle.red, label="Close", emoji='⚔️'),],)

	def check(res):
		return message.author == res.user and res.channel == message.channel 

	try:
		res = await bot.wait_for("button_click", check=check, timeout=60)
		if res.component.label == 'Close':
			await m.delete()
	except asyncio.TimeoutError:
		await m.edit(components=[Button(style=ButtonStyle.red, label="Close", emoji=bot.get_emoji(844701344719962132), disabled=True),]) 

@bot.event
async def on_guild_channel_create(channel):
	print('updating muted role channel perms...')
	guild = channel.guild
	role = discord.utils.get(guild.roles, name="Speaking Cut")
	if not role:
			print('creating role...')
			role = await guild.create_role(name="Speaking Cut")
			permissions = discord.Permissions()
			permissions.update(send_messages = False)

			await role.edit(reason = None, colour = discord.Colour.black(), permissions=permissions)
			print('Changing perms')
			for channel in guild.channels:
				await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
	else:
		await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
	print('success!')

	await bot_channel_tbl.add_channel(channel.id)
	await xp_channel_tbl.add_channel(channel.id)

@bot.event
async def on_guild_join(guild):
	global guild_ids
	guild_ids.append(guild.id)
	prefix_tbl.add_prefix(guild.id, ";")
	role = discord.utils.get(guild.roles, name="Speaking Cut")
	if not role:
		print('creating role...')
		role = await guild.create_role(name="Speaking Cut")
		permissions = discord.Permissions()
		permissions.update(send_messages = False)

		await role.edit(reason = None, colour = discord.Colour.black(), permissions=permissions)
		print('Changing perms')
		for channel in guild.channels:
			await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
	else:
		await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True, read_messages=True)
	print('success!')

@bot.event
async def on_command_error(ctx, error):
	await error_handling.handle_error(ctx, error)

##########
#Commands
##########

@bot.command()
@commands.check(is_botchannel)
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
		else:
			raise e
	coroutines=[result.run(ctx) for result in results]
	await asyncio.gather(*coroutines)

@bot.command()
async def rate(ctx, *, thing):
	h=hash(thing)%11
	embed=YoumuEmbed(title='Rate',description=f"I would rate *{thing}* a {h} out of 10", colour=0xcc00ff)
	await ctx.send(embed=embed)

@bot.command()
@commands.check(is_botchannel)
async def percent(ctx, *, thing):
	h=hash(str(ctx.author.id)+f' {thing}')%101
	embed=YoumuEmbed(title='Rate',description=f"{ctx.author.mention}, you are {h}% {thing}",colour=0xcc00ff)

	await ctx.send(embed=embed)

@bot.command()
@commands.check(is_botchannel)
async def ttt(ctx, player: discord.Member):
	if player.id==ctx.author.id:
		await ctx.send("You can't challenge yourself!")
	
	embed=YoumuEmbed(title='✉️Invitation!✉️', description=f'{player.mention}, {ctx.author.mention} has challenged you to a game of **Tic Tac Toe**. \n\nPress the button within the next minute to start the game. \n\n*Remember that if you don\'t accept, you might lose a friend~*', color=0x53cc74)
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
		
@bot.command(name='uno', aliases=['nou', 'no_u'])
@commands.check(is_botchannel)
async def one(ctx, *players: discord.Member):
	if not len(players) or (len(set(players))==1 and ctx.author in players):
		embed=YoumuEmbed(title='Woops!', description=f"You can't play **Uno** by yourself!", color=0xff0f1d)

		await ctx.send(embed=embed)
		return
	
	game=uno.UnoGame(ctx, bot, *players)
	await game.invite()
@bot.command()
@commands.check(is_botchannel)
async def inspire(ctx):
	try:
		url = 'http://inspirobot.me/api?generate=true'
		params = {'generate': 'true'}
		response = requests.get(url, params, timeout=10)
		image = response.text
		embed=YoumuEmbed(title='Inspiration', colour=0x53cc74)
		embed.set_image(url=image)

		await ctx.send(embed=embed)

	except RequestException:

		await ctx.send('Inspirobot is broken, there is no reason to live.')

@bot.command()
@commands.check(is_botchannel)
async def skin(ctx, username):
	sg = skingrabber()
	uuid = sg.get_uuid(user=username)
	print(uuid)
	render = f"https://visage.surgeplay.com/full/832/{uuid}"
	await ctx.send(render)

@bot.command()
@commands.check(is_botchannel)
async def help(ctx):
	embed=YoumuEmbed(title='Help',description=f"Check out the documentation that contains the help here:", color=0x53cc74)
	await ctx.send(embed=embed, components=[Button(style=ButtonStyle.URL, label="Github", url="https://github.com/4gboframram/Youmu-bot-")])

@bot.command()
async def amogus(ctx):
	await ctx.send('ඞ')
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
@commands.check(is_botchannel)
async def _help(ctx):
	embed=YoumuEmbed(title='Help',description=f"Check out the documentation that contains the help here: https://github.com/4gboframram/Youmu-bot-", color=0x53cc74)
	await ctx.send(embed=embed)
	

@slash.slash(name="rate", description='What would I rate [thing] out of 10?', guild_ids=guild_ids)
@commands.check(is_botchannel)
async def _rate(ctx, *, thing):
	h=hash(thing)%11
	embed=YoumuEmbed(title='Rate',description=f"I would rate *{thing}* a {h} out of 10",colour=0xcc00ff)
	await ctx.send(embed=embed)

@slash.slash(name="ping", description='Pong?', guild_ids=guild_ids)
@commands.check(is_botchannel)
async def _ping(ctx: SlashContext):
	await ctx.send(f'{choice(ping_messages)} ({round(bot.latency*1000, 2)}ms)')

@slash.slash(name="inspire", description='Inspiration anyone? (Generated using Inspirobot)', guild_ids=guild_ids)
@commands.check(is_botchannel)
async def _inspire(ctx):

	try:
		url = 'http://inspirobot.me/api?generate=true'
		params = {'generate': 'true'}
		response = requests.get(url, params, timeout=10)
		image = response.text
		embed=YoumuEmbed(title='Inspiration', colour=0x53cc74)
		embed.set_image(url=image)
		await ctx.send(embed=embed)

	except RequestException:
		await ctx.send('Inspirobot is broken, there is no reason to live.')

##################
# Leveling Commands
#################

@bot.command()
@commands.check(is_botchannel)
async def xp(ctx):
	stats = await levels_tbl.get_member_stats(ctx.guild.id, ctx.author.id)
	needed = db.LevelsTable.needed_exp_to_levelup(stats.level + 1) - stats.exp
	embed = YoumuEmbed(title='Xp?', description=f"{ctx.author.mention}, you are level {stats.level}, and {needed} xp from leveling up.", color=0x53cc74)
	await ctx.send(embed=embed)

@bot.command()
@commands.check(is_botchannel)
async def rank(ctx):
	rank = await levels_tbl.get_member_rank(ctx.guild.id, ctx.author.id)
	embed = YoumuEmbed(title='Rank?', description=f"{ctx.author.mention}, you are rank {rank} in the server!", color=0x53cc74)
	await ctx.send(embed=embed)



##########
# xp control commands
##########
@bot.command()
@commands.has_permissions(administrator=True)
async def addxpchannel(ctx):
	if await xp_channel_tbl.add_channel(ctx.channel.id):
		embed = YoumuEmbed(title=f"Xp Channel", description=f"Channel {ctx.channel.mention} is now an xp channel.", colour=0xadf0ff)	
		await ctx.send(embed=embed)
	else: 
		embed = YoumuEmbed(title=f"Error", description=f"Channel {ctx.channel.mention} is already an xp channel, baka.", colour=0xff0000)	
		await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def removexpchannel(ctx):
	if await xp_channel_tbl.remove_channel(ctx.channel.id):
		embed = YoumuEmbed(title=f"Xp Channel", description=f"Channel {ctx.channel.mention} is no longer an xp channel.", colour=0xadf0ff)	
		await ctx.send(embed=embed)
	else:
		embed = YoumuEmbed(title=f"Xp Channel Error", description=f"Could not remove this channel from the list of xp channels because it is not a xp channel to begin with, baka.", colour=0xff0000)	
		await ctx.send(embed=embed)
	
@bot.command()
@commands.has_permissions(administrator=True)
async def allxpchannel(ctx):
	await xp_channel_tbl.add_multiple_channels(channel.id for channel in ctx.guild.text_channels)
	embed = YoumuEmbed(title=f"Xp Channel", description=f"All channels are now xp channels", colour=0xadf0ff)		
	await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def removeallxpchannels(ctx):
	await xp_channel_tbl.remove_multiple_channels(channel.id for channel in ctx.guild.text_channels)
	embed = YoumuEmbed(title=f"Xp Channel", description=f"All xp channels have been removed", colour=0xadf0ff)	
	await ctx.send(embed=embed)


#####################
# Bot Channel Commands
#####################

@bot.command()
@commands.has_permissions(administrator=True)
async def addbotchannel(ctx):
	if await bot_channel_tbl.add_channel(ctx.channel.id):
		embed = YoumuEmbed(title=f"Bot Channel", description=f"Channel {ctx.channel.mention} is now a bot channel. If you had no bot channels before, then this is the only channel where this bot's commands can be used", colour=0xadf0ff)	
		await ctx.send(embed=embed)
	else: 
		embed = YoumuEmbed(title=f"Error", description=f"Channel {ctx.channel.mention} is already a bot channel, baka", colour=0xff0000)	
		await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def removebotchannel(ctx):
	if await bot_channel_tbl.remove_channel(ctx.channel.id):
		embed = YoumuEmbed(title=f"Xp Channel", description=f"Channel {ctx.channel.mention} is no longer an xp channel.", colour=0xadf0ff)	
		await ctx.send(embed=embed)
	else:
		embed = YoumuEmbed(title=f"Xp Channel Error", description=f"Could not remove this channel from the list of xp channels because it is not a xp channel to begin with, baka.", colour=0xff0000)	
		await ctx.send(embed=embed)
	
@bot.command()
@commands.has_permissions(administrator=True)
async def allbotchannel(ctx):
	await bot_channel_tbl.add_multiple_channels(channel.id for channel in ctx.guild.text_channels)
	embed = YoumuEmbed(title=f"Bot Channel", description=f"All channels are now bot channels", colour=0xadf0ff)		
	await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def removeallbotchannels(ctx):
	await bot_channel_tbl.remove_multiple_channels(channel.id for channel in ctx.guild.text_channels)
	embed = YoumuEmbed(title=f"Bot Channel", description=f"All bot channels have been removed", colour=0xadf0ff)	
	await ctx.send(embed=embed)

#########
# Prefix
#########
@bot.command()
async def prefixes(ctx):
	prefix = await prefix_tbl.get_prefixes(ctx.guild.id)
	prefix_str = '\n'.join(prefix)
	print(prefix_str)
	embed = YoumuEmbed(title='Prefixes', description=f'Prefixes: \n**{prefix_str}**', color=0x53cc74)
	await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def addprefix(ctx, prefix):
	if await prefix_tbl.add_prefix(ctx.guild.id, prefix):
		embed = YoumuEmbed(title=f"Prefix Add!", description=f"Added '{prefix}' to the list of prefixes", colour=0xadf0ff)	
	else:
		embed=YoumuEmbed(title=f"Prefix Error", description=f"That prefix is already a supported prefix!", colour=0xff0000)	
	await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def removeprefix(ctx, prefix):
	if await prefixes_tbl.remove_prefix(ctx.guild.id, prefix):
		embed = YoumuEmbed(title=f"Prefix Removed!", description=f"Removed '{prefix}' from the list of prefixes", colour=0xadf0ff)	
	else:
		embed = YoumuEmbed(title=f"Prefix Error", description=f"Could not remove the prefix '{prefix}' because it is not a prefix to begin with, baka.", colour=0xff0000)	
	await ctx.send(embed=embed)

################
# Sauce
##############

@bot.command(name='gelbooru', aliases=['gb'])
@commands.check(is_botchannel)
async def gelbooru(ctx, arg=''):
	await sauces.char(ctx, arg)

@bot.command(name='gelboorunf', aliases=['gbnf', 'gbnsfw'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def gelbooru_nofilter(ctx, arg=''):
	await sauces.char(ctx, arg, nsfw=True)

@bot.command(name='gelboorua', aliases=['gba', 'gbanimated', 'gbanim'])
@commands.check(is_botchannel)
async def gelbooruanimated(ctx, arg=''):
	await sauces.char(ctx, arg, animated=True)

@bot.command(name='gelbooruanf', aliases=['gbanf', 'gbansfw', 'gbanimatednf', 'gbanimatednsfw', 'gbanimnf', 'gbanimnsfw'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def gelbooruanimated_nofilter(ctx, arg=''):
	await sauces.char(ctx, arg, nsfw=True, animated=True)

@bot.command()
@commands.check(is_botchannel)
async def youmu(ctx):
	await sauces.char(ctx, 'konpaku_youmu')

@bot.command(name='youmunf')
@commands.check(is_botchannel)
@commands.is_nsfw()
async def youmu_nofilter(ctx):
	await sauces.char(ctx, 'konpaku_youmu', nsfw=True)

@bot.command(aliases=['yuyu'])
@commands.check(is_botchannel)
async def yuyuko(ctx):
	await sauces.char(ctx, 'saigyouji_yuyuko')

@bot.command(name='yuyukonf', aliases=['yuyunf'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def yuyu_nofilter(ctx):
	await sauces.char(ctx, 'saigyouji_yuyuko', nsfw=True)

@bot.command(aliases=['flan'])
@commands.check(is_botchannel)
async def flandre(ctx):
	await sauces.char(ctx, 'flandre_scarlet')

@bot.command(name='flandrenf', aliases=['flannf'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def flandre_nofilter(ctx):
	await sauces.char(ctx, 'flandre_scarlet', nsfw=True)

@bot.command(aliases=['remi'])
@commands.check(is_botchannel)
async def remilia(ctx):
	await sauces.char(ctx, 'remilia_scarlet')

@bot.command(name='remilianf', aliases=['reminf'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def remilia_nofilter(ctx):
	await sauces.char(ctx, 'remilia_scarlet', nsfw=True)

@bot.command()
@commands.check(is_botchannel)
async def marisa(ctx):
	score_rng=randint(0,5)
	await sauces.char(ctx, f'kirisame_marisa+score:>={score_rng}')

@bot.command(name='marisanf')
@commands.check(is_botchannel)
@commands.is_nsfw()
async def marisa_nofilter(ctx):
	score_rng=randint(0,5)
	await sauces.char(ctx, f'kirisame_marisa+score:>={score_rng}', nsfw=True)

@bot.command(name='reimu', aliases=['miko'])
@commands.check(is_botchannel)
async def reimu(ctx):
	score_rng=randint(0,5)
	await sauces.char(ctx, f'Hakurei_Reimu+score:>={score_rng}')

@bot.command(name='reimunf', aliases=['mikonf'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def reimu_nofilter(ctx):
	score_rng=randint(0,5)
	await sauces.char(ctx, f'Hakurei_Reimu+score:>={score_rng}', nsfw=True)

@bot.command(name='sakuya')
@commands.check(is_botchannel)
async def sakuya(ctx):
	score_rng=randint(0,5)
	await sauces.char(ctx, f'izayoi_sakuya+-id:5237460+score:>={score_rng}')

@bot.command(name='sakuyanf')
@commands.check(is_botchannel)
@commands.is_nsfw()
async def sakuya_nofilter(ctx):
	score_rng=randint(0,5)
	await sauces.char(ctx, f'izayoi_sakuya+-id:5237460+score:>={score_rng}', nsfw=True)

@bot.command(aliases=['patchy'])
@commands.check(is_botchannel)
async def patchouli(ctx):
	await sauces.char(ctx, 'patchouli_knowledge')

@bot.command(name='patchoulinf', aliases=['patchynf'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def patchouli_nofilter(ctx):
	await sauces.char(ctx, 'patchouli_knowledge', nsfw=True)

@bot.command(aliases=['baka', 'thestrongest'])
@commands.check(is_botchannel)
async def cirno(ctx):
	await sauces.char(ctx, 'cirno')

@bot.command(name='cirnonf', aliases=['bakanf', 'thestrongestnf'])
@commands.check(is_botchannel)
@commands.is_nsfw()
async def cirno_nofilter(ctx):
	await sauces.char(ctx, 'cirno', nsfw=True)

@bot.command()
@commands.check(is_botchannel)
async def satori(ctx):
	await sauces.char(ctx, 'komeiji_satori')

@bot.command(name='satorinf',)
@commands.check(is_botchannel)
@commands.is_nsfw()
async def cirno_nofilter(ctx):
	await sauces.char(ctx, 'komeiji_satori', nsfw=True)

@bot.command(name='char')
@commands.check(is_botchannel)
async def char(ctx, *, tag):
	await sauces.char(ctx, tag)

@bot.command(name='charnf')
@commands.check(is_botchannel)
@commands.is_nsfw()
async def char_nofilter(ctx, tag):
	await sauces.char(ctx, tag, nsfw=True)

########
#Owner utils
#######
@bot.command()
@commands.is_owner()
async def owner(ctx, guild_id: int, *, message):
	guild = bot.get_guild(guild_id)
	"""owner=guild.owner
	print(owner)
	await ctx.author.send(str(owner))"""
	channel = guild.text_channels[1]
	print(channel)
	await channel.send(message)
	print('message sent')
	print(await channel.invites())
	print("got invites")
	invite=await channel.create_invite()
	print(invite.url)

	await ctx.author.send(invite.url)

async def setup():
	global levels_tbl, bot_channel_tbl, xp_channel_tbl, prefixes_tbl
	conn = await aiosqlite.connect("databases/youmu.db")
	levels_tbl = db.LevelsTable(conn)
	bot_channel_tbl = db.BotChannelsTable(conn)
	xp_channel_tbl = db.ExpChannelsTable(conn)
	prefixes_tbl = db.PrefixTable(conn)

if __name__ == "__main__":
	asyncio.get_event_loop().run_until_complete(setup())
	bot.run(TOKEN)
