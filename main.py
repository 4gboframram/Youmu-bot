import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
from parser import parse, CommandSyntaxError, CommandUnexpectedEOF
import asyncio
from random import choice
bot = commands.Bot(command_prefix=";",help_command=None)
ping_messages=['There\'s nothing my Roukanken can\'t cut!',"Everyone talks about my sword Roukanken, but not my other sword Hakurouken. *sad Hakurouken noises* ", "Everyone always says 'Youmu best girl', but not 'How is best girl?' :(", "Me or Reimu? That's like asking 'would you rather a brown-haired broke girl or a sweet wife.'", 'Dammit Yuyuko-sama. The fridge is empty again.', 'If it taste bad I can always shove this up your ass~', 'I cut the heavens. I cut reason. I even cut time itself.']
@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected')
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
	
@bot.command()
async def ping(ctx):
	await ctx.send(choice(ping_messages))

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
async def rate(ctx, thing):
	h=hash(thing)%11
	embed=discord.Embed(title='Rate',description=f"I would rate *{thing}* a {h} out of 10",colour=0xcc00ff)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)

@bot.command()
async def percent(ctx, thing):
	h=hash(str(ctx.author.id)+f' {thing}')%101
	embed=discord.Embed(title='Rate',description=f"{ctx.author.mention}, you are {h}% {thing}",colour=0xcc00ff)
	embed.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
	await ctx.send(embed=embed)

keep_alive()
bot.run(os.getenv('TOKEN'))