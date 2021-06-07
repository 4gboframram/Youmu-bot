import discord
from discord.ext import commands
from constants import YoumuEmbed
async def handle_error(ctx, error):
		# if command has local error handler, return
		if hasattr(ctx.command, 'on_error'):
			return

		# get the original exception
		error = getattr(error, 'original', error)

		if isinstance(error, commands.CommandNotFound):
			embed = YoumuEmbed(title="You messed up",description="That command does not exist, you baka.\n ", colour=0xff0000)
			embed.add_field(name='Technical details for the nobody that cares', value='Error: `commands.CommandNotFound`')
			await ctx.send(embed=embed)
			return

		if isinstance(error, commands.BotMissingPermissions):
			missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
			if len(missing) > 2:
				fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
			else:
				fmt = ' and '.join(missing)
			_message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
			embed = YoumuEmbed(title="You or the moderators messed up",description=_message, colour=0xff0000)
			embed.add_field(name='Technical details for the nobody that cares:', value='Error: `commands.BotMissingPermissions`')
			await ctx.send(embed=embed)
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send('This command has been disabled.')
			return

		if isinstance(error, commands.MissingPermissions):
			missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
			if len(missing) > 2:
				fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
			else:
				fmt = ' and '.join(missing)
			_message = 'You need the **{}** permission(s) to use this command, you baka.'.format(fmt)
			embed = YoumuEmbed(title="You or the moderators messed up",description=_message, colour=0xff0000)
			embed.add_field(name='Technical details for the nobody that cares:', value='Error: `commands.MissingPermissions`')
			await ctx.send(embed=embed)
			return

		if isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send('This command cannot be used in direct messages.')
			except discord.Forbidden:
				pass
			return

		if isinstance(error, commands.CheckFailure):
			embed = YoumuEmbed(title="You or the moderators messed up",description="You do not have permission to use this command.", colour=0xff0000)
			embed.add_field(name='Technical details for the nobody that cares:', value='Error: `commands.CheckFailure`')
			await ctx.send(embed=embed)
			return 
		
		if isinstance(error, commands.MissingRequiredArgument):
			embed = YoumuEmbed(title="You messed up",description=f"Missing `{error.param}` parameter in command.", colour=0xff0000)
			embed.add_field(name='Technical details for the nobody that cares:', value='Error: `commands.MissingRequiredArgument`')
			await ctx.send(embed=embed)
			return 