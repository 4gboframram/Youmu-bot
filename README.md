# About
This is Youmu bot, a wip Discord bot with many functionalities.

This started as just a moderation bot where all of its moderation commands are built into a single command: `;cut` (or `/cut` if you're into that sort of thing), but has turned into a lot more. 

## Inspiration
One day, my friend who roleplays as Youmu joined my Discord server. I was thinking about making a Discord bot for them and they agreed that I should make one. Then I brought up a stupid idea: What if I made a Discord bot where all of the commands are in a single command? I thought about it overnight and concluded it was a stupid, yet fun idea. It would allow me to get familiar with creating lexers and parsers.


# Commands:
**Now slash commands are implemented for some commands**
**New: Now mentioning the bot is now a valid prefix**

The main command of this bot is `;cut` It is basically a Swiss army knife of moderation. This command has all of the following functionalities built in:  ban, mute, tempmute, change role perms, change role color, delete role, purge a channel, lock a channel, and finally slice people that you don't like in half (or you can kill yourself too if you're a typical suicidal weeb like the target audience of this bot)

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

### Bot Channels

For this bot, as the name implies, a bot channel is a channel where users can interact with the bot. **By default all channels in your server are bot channels.** 

When a channel is removed from the list of bot channels, all of the commands except `;cut`, `;help`, and the commands below that manage bot channels are disabled and the bot sends an embed to let the invokee of the command know that they cannot use the command there.

To manage bot channels, you need `administrator` permissions

`;addbotchannel` : adds a channel to the list of bot channels

`;removebotchannel` : removes a channel from the list of bot channels

`;allbotchannel` : makes every channel in the server a bot channel

`;removeallbotchannels` : removes every channel from the server from the list of bot channels


### Leveling System:

Xp is a way to quantify a person's activity and devotion to a server. By sending messages, you gain xp. You can check out your xp stats with these commands:

`;xp` : See how much xp you have until the next level

`;rank` : See what your current rank in the server is.

The amount of xp you get per message sent is inversely proportional to the amount of messages the member has sent in the last minute. This is to prevent people from just spamming messages to receive large amounts of xp, but to show who is truly most devoted to the server

### Xp Channels

An xp channel, as the name suggests, is a channel where you can gain xp. **By default all channels in the server are xp channels.**

To manage xp channels, like bot channels, you need `administrator` permissions

`;addbotchannel` : adds a channel to the list of bot channels

`;removebotchannel` : removes a channel from the list of bot channels

`;allbotchannel` : makes every channel in the server a bot channel

`;removeallbotchannels` : removes every channel from the server from the list of bot channels

### Games:
`;ttt [player]` : Challenge a user to a game of Tic Tac Toe. 

`;uno [list of players]` : Challenge that group of players to uno. If a member is mentioned more than once, then it will only put them in once. **Warning: Uno is still pretty buggy and will also spam dms.** Alternative aliases: `no_u`, `nou`

### Art Finding (Gelbooru)
These are commands that can be used to search for random art on [Gelbooru](gelbooru.com) for a character. There is a version of each command with an NSFW filter, and one without the filter that can only be used in NSFW channels. 

**As with all NSFW filters, this will never be perfect, no matter how many tags or artists you exclude. The developer of this bot is not responsible for any harm done to the users of this bot when using commands.** 

The filter is identical to the one used in [Tenshi Bot](https://github.com/KawashiroDev/TenshiBot/).

Now that the disclaimers are out of the way, here are the commands:

`;char [tag]` : search Gelbooru for random art with that tag, usually a character. This uses the NSFW filter. **This should use underscores (_) in the tag and not spaces and should be surrounded by quotes just in case.** If you are using multiple tags, the tags should be inputted the same way they are put into the url of the browser.

`;charnf [tag]` : same as `;char` but without the NSFW filter.

Since this bot is directed towards the Touhou fandom, there are some extra aliases for searching art of a few different popular characters provided below. 

You can get the version with no NSFW filter by appending 'nf' to the end. In parenthesis are other aliases for the character in addition to the name given. **The name of the characters here are capitalized for neatness, but should be lowercase when inputting the command**

**List of Characters**

- Reimu `(miko)`
- Marisa
- Flandre `(flan)`
- Remilia `(remi)`
- Youmu
- Yuyuko `(yuyu)`
- Sakuya
- Patchouli `(patchy)`
- Cirno `(baka, thestrongest)`
- Satori
### Other Commands: 

These commands are for extra fun and for things that wouln't fit into the main `;cut` command or any of the other categories. They are just quick, simple, and enjoyable little things.

`;ping`: Test to see if the bot is online and get the ping in miliseconds. In return, you get a funny Youmu message.

`;rate "[thing]"`: Rates a thing out of 10. *For technical details, this is computed by taking the hash of the `[thing]` argument mod 11, or with code: `hash(thing)%11`*

`;percent "[thing]"`: Tells you what percent `[thing]` you are. 

*For technical details, this is computed by taking the hash of the concantenation of the user's id and the thing with a space between them mod 101, or with actual code: `hash(f"{userid} {thing}")%101`* 

`;inspire`:  Generates an (un)inspirational quote with [Inspirobot's API](https://inspirobot.me/)

`;skin [mc user]`: get a 3-dimensional rendering of a Minecraft player's skin 
# How to add to your server

You can ask me on discord RamRam#0001 to send you an invite link, but I may decline. I do not have the link public since the bot is unable to get verified and is capped to 100 servers

Currently, since I am not old enough to verify any of my Discord bots without parental consent (which they do not consent), you have to download this yourself and host it. I use replit for hosting since it is the easiest way for me to be able to code while at school. 

However, It is really easy to host with replit, you can just fork [this repl](https://replit.com/@4gboframram/Youmu-bot) and create a secret named `TOKEN` with the value of another bot's token. Give the bot admin priveleges in the discord developer portal, hit run and go to [uptimerobot](https://uptimerobot.com/) and make an http monitor that pings the site the repl creates every at least 30 minutes to keep the repl online almost 24/7. Now all you have to do is invite the bot to your server and you're done. (Also the repl has wip features that may or may not be documented or may not work if you fork it while I'm still working on it)

For self-hosting, clone this github repo, go to `main.py` and delete `from keep_alive import keep_alive` and `keep_alive()` because if you just keep those in the code you'll be hosting an unnecessary web app that does nothing for you and wasting memory and cpu. Create a `.env` that contains `TOKEN=[token]` where `[token]` is your bot's token. 
