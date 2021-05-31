# About
This is Youmu bot, a wip Discord bot where all of its moderation commands are built into a single command: `;cut `

## Inspiration
One day, my friend who roleplays as Youmu joined my Discord server. I was thinking about making a Discord bot for them and they agreed that I should make one. Then I brought up a stupid idea: What if I made a Discord bot where all of the commands are in a single command? I thought about it overnight and concluded it was a stupid, yet fun idea. It would allow me to get familiar with creating lexers and parsers.

# Commands:

The main command of this bot is `;cut` This command has all of the following functionalities built in:  ban, mute, tempmute, change role perms, change role color, delete role, purge a channel, lock a channel, and finally slice people that you don't like in half (or you can kill yourself too if you're a typical suicidal weeb like the target audience of this bot)

## ;cut
### How the `;cut` command works (and rational behind it)
Basically there are 3 different types of mentions on Discord: channel, role, and member.

For this command, I took the approach of having multiple different levels of commands per type of mention. **The base levels are as follows:**

**Channel: clear a given amount of messages from the channel**

**Role: toggle a permission for that role** (not all permissions are implemented yet because some of them should require more thought than just using a command to grant them)

**Member: mute or tempmute** (depending on the arguments for the command)

Then there are 2 operators that can operate on those mentions: extend ('+') and reduce ('-'). These act as prefixes for the mention. The extend operator increases the power of the command, and the reduce decreases the power of the command.

You also can put comments after your command by placing a ; after the command and placing your comment after. This does not affect the command at all, but you can do it anyways.  I left it in while I was bugfixing the parser in the command line.

**You can also execute multiple subcommands in a single command.** This can be useful for muting or banning multiple members at the same time, for example and mostly shows what is possible with a custom parser.

### List of actions for the cut command:

#### No operator:

`;cut [member] *{[integer][smhd]}`: mutes the member for a that amount of time if given. If no time given, mutes the permanently. Also if used on a muted member, it unmutes the member. Personally, I wouldn't use more than an hour mute just in case the bot goes down

`;cut [channel] {number of messages}`: Deletes that number of messages from the given channel.

`;cut [role] {permission}`: Toggles the given permission of a role. 

List of perms that are currently supported:
- add_reactions
- kick_members
- ban_members
- external_emojis
- manage_emojis
- change_nickname
- manage_nicknames
- mention_everyone

#### Extend Operator:

`;cut + [member]`: bans the member **THIS WILL NOT UNBAN A MEMBER**

`;cut + [channel]`: prevents anyone from speaking in the channel from speaking until this command is run again.

`;cut + [role]`: Deletes the role

#### Reduce Operator:

`;cut - [member]`: Slice the member in half with a cool Youmu gif

`;cut - [role]`: Change a role's color to a value in hexadecimal. A preview of the color is also sent to the channel for future reference

### Other Commands: 

These commands are for extra fun and for things that wouln't fit into the main `;cut` command. 

`;ping`: Test to see if the bot is online. In return you get a funny Youmu message.

`;rate "[thing]"`: Rates a thing out of 10. *For technical details, this is computed by taking the hash of the `[thing]` argument mod 11.*

`;percent "[thing]"`: Tells you what percent `[thing]` you are. 

*For technical details, this is computed by taking the hash of the concantenation of the user's id and the thing with a space between them mod 101, or with f-string notation: `hash(f"{userid} {thing}")%101`* 




