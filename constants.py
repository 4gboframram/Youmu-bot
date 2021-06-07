from discord import Embed
class Constants:
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

class YoumuEmbed(Embed): #Basically like a macro that creates an embed with the proper author
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.set_author(name="Youmu Bot", icon_url='https://cdn.discordapp.com/avatars/847655832169480222/16c78890f9383ec318b4560675410120.webp?size=2048')
		