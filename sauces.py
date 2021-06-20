import discord
import aiohttp
from bs4 import BeautifulSoup
import random
import asyncio
import os
import sys

booruappend = ''
booru = 'gelbooru.com'
#base tags to apply to all levels (except gifs)
boorutags_base = 'solo+rating:safe+-6%2Bgirls+-comic+-greyscale+-huge_filesize+-animated+-audio+-webm+-absurdres+-monochrome'
#artists whose works slip by the tag filters
badartists = '+-nori_tamago+-shiraue_yuu+-hammer_(sunset_beach)+-roke_(taikodon)+-guard_bento_atsushi+-kushidama_minaka+-manarou+-shounen_(hogehoge)+-fusu_(a95101221)+-guard_vent_jun+-teoi_(good_chaos)+-wowoguni+-yadokari_genpachirou+-hydrant_(kasozama)+-e.o.+-fusu_(a95101221)+-nishiuri+-freeze-ex+-yuhito_(ablbex)+-koto_inari'
#base tags for gif command
boorutags_gif = 'rating:safe+-6%2Bgirls+-comic+-greyscale+-huge_filesize+-audio+-webm+-absurdres'
#default blacklisted tags (full SFW mode)
badtags_strict = "-underwear+-sideboob+-pov_feet+-underboob+-upskirt+-sexually_suggestive+-ass+-bikini+-spread_legs+-bdsm+-lovestruck+-artificial_vagina+-swimsuit+-covering_breasts+-huge_breasts+-blood+-penetration_gesture+-seductive_smile+-no_bra+-off_shoulder+-breast_hold+-cleavage+-nude+-butt_crack+-naked_apron+-convenient_censoring+-bra+-trapped+-restrained+-skirt_lift+-open_shirt+-underwear+-evil_smile+-evil_grin+-choker+-head_under_skirt+-skeleton+-open_fly+-o-ring_bikini+-middle_finger+-white_bloomers+-hot+-tank_top_lift+-short_shorts+-alternate_breast_size+-belly+-wind_lift+-you_gonna_get_raped+-convenient_leg+-convenient_arm+-downblouse+-torn_clothes+-sweater_lift+-open-chest_sweater+-bunnysuit+-gag+-gagged+-ball_gag+-hanging+-erect_nipples+-head_out_of_frame+-covering+-skirt_around_ankles+-furry+-shirt_lift+-vest_lift+-lifted_by_self+-when_you_see_it+-feet+-thighs+-skirt_hold+-open_dress+-open_clothes+-naked_shirt+-shirt_tug+-hip_vent+-no_panties+-surprised+-onsen+-naked_towel+-have_to_pee+-skirt_tug+-pole_dancing+-stripper_pole+-dimples_of_venus+-topless+-trembling+-no_humans+-creepy+-showgirl_skirt+-cookie_(touhou)+-pov+-fusion+-drugs+-weed+-forced_smile+-mouth_pull+-groin+-corruption+-dark_persona+-arms_behind_head+-crop_top+-gluteal_fold+-pregnant+-younger+-white_swimsuit+-tsundere+-crying+-naked_sheet+-undressing+-parody+-under_covers+-genderswap+-real_life_insert+-what+-confession+-race_queen+-naked_cloak+-latex+-bodysuit+-nazi+-swastika+-strap_slip+-chemise+-see-through+-dark+-bad_anatomy+-poorly_drawn+-messy+-you're_doing_it_wrong+-midriff+-large_breasts+-embarrassed+-smelling+-chains+-collar+-arms_up+-blurry_vision+-obese+-miniskirt"
#tags to blacklist in TenshiBot Hangout
#tags to blacklist in moderate mode
idtext = 'Gbooru ID'


async def char(ctx, char):
		em = discord.Embed(title=' ', description=' ', colour=random.randint(0,0xFFFFFF))
		
		booruurl = 'http://' + booru + '/index.php?page=dapi&s=post&q=index&tags=' + boorutags_base + badtags_strict + badartists + '+' + char
		embed_name = 'Character!'
		async with aiohttp.ClientSession() as session:
			async with session.get(booruurl) as r:
				if r.status == 200:
					soup = BeautifulSoup(await r.text(), "lxml")
					num = int(soup.find('posts')['count'])
					maxpage = int(round(num/100))
					page = random.randint(0, maxpage)
					t = soup.find('posts')
					p = t.find_all('post')
					source = ((soup.find('post'))['source'])
					if num < 100:
						pic = p[random.randint(0,num-1)]
					elif page == maxpage:
						pic = p[random.randint(0,99)]
					else:
						pic = p[random.randint(0,99)]
					msg = pic['file_url']
					booru_id = pic['id']
					booru_tags = pic['tags']
					booru_sauce = pic['source']
					img_width = pic['width']
					img_height = pic['height']
					creator = pic['creator_id']
					if booru_sauce == '':
						booru_sauce = 'No source listed'
					if "hentai" in booru_sauce:
						booru_sauce = "Source hidden\n(NSFW website)"
					if "pixiv" in booru_sauce:
						booru_sauce = "[Pixiv](" + booru_sauce + ")"
					if "twitter" in booru_sauce:
						booru_sauce = "[Twitter](" + booru_sauce + ")"
					if "nicovideo" in booru_sauce:
						booru_sauce = "[NicoNico](" + booru_sauce + ")"
					if "deviantart" in booru_sauce:
						booru_sauce = "[DeviantArt](" + booru_sauce + ")"

					em.set_author(name=embed_name)
					em.set_image(url=booruappend + msg)
					em.add_field(name="Image source", value=booru_sauce, inline=False)	
					em.add_field(name=idtext, value=booru_id, inline=True)
					em.add_field(name="Dimensions", value=img_width + "x" + img_height, inline=True)
					await asyncio.sleep(0.15)
					booru_img = await ctx.send(embed=em)

async def char_nofilter(ctx, char):
		em = discord.Embed(title=' ', description=' ', colour=random.randint(0,0xFFFFFF))
		
		booruurl = 'http://' + booru + '/index.php?page=dapi&s=post&q=index&tags=' + boorutags_base.replace('rating:safe', '-rating:safe') + '+' + char
		embed_name = 'No filter, huh?'
		async with aiohttp.ClientSession() as session:
			async with session.get(booruurl) as r:
				if r.status == 200:
					soup = BeautifulSoup(await r.text(), "lxml")
					num = int(soup.find('posts')['count'])
					maxpage = int(round(num/100))
					page = random.randint(0, maxpage)
					t = soup.find('posts')
					p = t.find_all('post')
					source = ((soup.find('post'))['source'])
					if num < 100:
						pic = p[random.randint(0,num-1)]
					elif page == maxpage:
						pic = p[random.randint(0,99)]
					else:
						pic = p[random.randint(0,99)]
					msg = pic['file_url']
					booru_id = pic['id']
					booru_tags = pic['tags']
					booru_sauce = pic['source']
					img_width = pic['width']
					img_height = pic['height']
					creator = pic['creator_id']
					if booru_sauce == '':
						booru_sauce = 'No source listed'
					if "pixiv" in booru_sauce:
						booru_sauce = "[Pixiv](" + booru_sauce + ")"
					if "twitter" in booru_sauce:
						booru_sauce = "[Twitter](" + booru_sauce + ")"
					if "nicovideo" in booru_sauce:
						booru_sauce = "[NicoNico](" + booru_sauce + ")"
					if "deviantart" in booru_sauce:
						booru_sauce = "[DeviantArt](" + booru_sauce + ")"

					em.set_author(name=embed_name)
					em.set_image(url=booruappend + msg)
					em.add_field(name="Image source", value=booru_sauce, inline=False)	
					em.add_field(name=idtext, value=booru_id, inline=True)
					em.add_field(name="Dimensions", value=img_width + "x" + img_height, inline=True)
					await asyncio.sleep(0.15)
					booru_img = await ctx.send(embed=em)
