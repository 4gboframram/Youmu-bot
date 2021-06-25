import asyncio
from aiohttp import ClientSession
from random import choice as random_choice, randint
from discord import Embed


#base tags to apply to all levels (except gifs)
boorutags_base = [
    '-rating:safe',
    'sort:random',
    'solo',
    '-6%2Bgirls',
    '-comic',
    '-greyscale',
    '-huge_filesize',
    '-animated',
    '-audio',
    '-webm',
    '-absurdres',
    '-monochrome'
]
#artists whose works slip by the tag filters
badartists = [
    '-nori_tamago',
    '-shiraue_yuu',
    '-hammer_(sunset_beach)',
    '-roke_(taikodon)',
    '-guard_bento_atsushi',
    '-kushidama_minaka',
    '-manarou',
    '-shounen_(hogehoge)',
    '-fusu_(a95101221)',
    '-guard_vent_jun',
    '-teoi_(good_chaos)',
    '-wowoguni',
    '-yadokari_genpachirou',
    '-hydrant_(kasozama)',
    '-e.o.',
    '-fusu_(a95101221)',
    '-nishiuri',
    '-freeze-ex',
    '-yuhito_(ablbex)',
    '-koto_inari',
]
#default blacklisted tags (full SFW mode)
badtags_strict = ['-underwear','-sideboob','-pov_feet','-underboob','-upskirt','-sexually_suggestive','-ass','-bikini','-spread_legs','-bdsm','-lovestruck','-artificial_vagina','-swimsuit','-covering_breasts','-huge_breasts','-blood','-penetration_gesture','-seductive_smile','-no_bra','-off_shoulder','-breast_hold','-cleavage','-nude','-butt_crack','-naked_apron','-convenient_censoring','-bra','-trapped','-restrained','-skirt_lift','-open_shirt','-underwear','-evil_smile','-evil_grin','-choker','-head_under_skirt','-skeleton','-open_fly','-o-ring_bikini','-middle_finger','-white_bloomers','-hot','-tank_top_lift','-short_shorts','-alternate_breast_size','-belly','-wind_lift','-you_gonna_get_raped','-convenient_leg','-convenient_arm','-downblouse','-torn_clothes','-sweater_lift','-open-chest_sweater','-bunnysuit','-gag','-gagged','-ball_gag','-hanging','-erect_nipples','-head_out_of_frame','-covering','-skirt_around_ankles','-furry','-shirt_lift','-vest_lift','-lifted_by_self','-when_you_see_it','-feet','-thighs','-skirt_hold','-open_dress','-open_clothes','-naked_shirt','-shirt_tug','-hip_vent','-no_panties','-surprised','-onsen','-naked_towel','-have_to_pee','-skirt_tug','-pole_dancing','-stripper_pole','-dimples_of_venus','-topless','-trembling','-no_humans','-creepy','-showgirl_skirt','-cookie_(touhou)','-pov','-fusion','-drugs','-weed','-forced_smile','-mouth_pull','-groin','-corruption','-dark_persona','-arms_behind_head','-crop_top','-gluteal_fold','-pregnant','-younger','-white_swimsuit','-tsundere','-crying','-naked_sheet','-undressing','-parody','-under_covers','-genderswap','-real_life_insert','-what','-confession','-race_queen','-naked_cloak','-latex','-bodysuit','-nazi','-swastika','-strap_slip','-chemise','-see-through','-dark','-bad_anatomy','-poorly_drawn','-messy',"-you're_doing_it_wrong",'-midriff','-large_breasts','-embarrassed','-smelling','-chains','-collar','-arms_up','-blurry_vision','-obese','-miniskirt',]

# Takes a booru (i.e. gelbooru.com) and returns a base API entry point
get_booru_base_url = lambda x: f'https://{x}/index.php?page=dapi&json=1&s=post&q=index&tags='
# Joins all the tags on the given list by a plus sign
join_tags = lambda x: "+".join(x)

async def char(ctx, character, booru='gelbooru.com', nsfw=False, animated=False):
    '''Searches he given character in gelbooru.com and returns a random result
    
    Args:
        ctx (Context): Instance of Discord's Context class
        character (str): Character to look for
        nsfw (bool): If true will return NSFW content, False by default
        animated (bool): If true will return gif content, False by default
    '''

    url = get_booru_base_url(booru)+join_tags([*boorutags_base, character])
    if not nsfw:
        url = url.replace('-rating:safe','rating:safe') + '+' + join_tags([*badtags_strict,*badartists])
    if animated:
        url = url.replace('-animated', 'animated')

    embed = Embed(title=' ', description=' ', colour=randint(0,0xFFFFFF))

    async with ClientSession() as session:
        async with session.get(url) as res:
            data = random_choice(await res.json())
            if not data:
                embed.set_author(name='Nothing found :(')
                await ctx.send(embed=embed)

    booru_sauce = data['source']

    if booru_sauce == '':
        booru_sauce = 'No source listed'
    elif "pixiv" in booru_sauce:
        booru_sauce = f'[Pixiv]({booru_sauce})'
    elif "twitter" in booru_sauce:
        booru_sauce = f'[Twitter]({booru_sauce})'
    elif "nicovideo" in booru_sauce:
        booru_sauce = f'[NicoNico]({booru_sauce})'
    elif "deviantart" in booru_sauce:
        booru_sauce = f'[DeviantArt]({booru_sauce})'
    
    embed.set_author(name='Character!')
    embed.set_image(url=data['file_url'])
    embed.add_field(name='Image source', value=booru_sauce, inline=False)    
    embed.add_field(name='Gelbooru ID', value=data['id'], inline=True)
    embed.add_field(name='Dimensions', value=f"{data['width']}x{data['height']}", inline=True)
    print('asd')
    await asyncio.sleep(0.15)
    await ctx.send(embed=embed)