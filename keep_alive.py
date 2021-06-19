# This file is used to keep the replit active
# If you're using replit, you can use this.
# To use, use uptimerobot to ping the
# site replit creates every at least 20 minutes

import asyncio
from aiohttp import web
import typing
import pathlib

routes = web.RouteTableDef()


@routes.get("/")
async def home():
    return web.Response(text="Bot is online")


async def keep_alive(address: typing.Union[pathlib.Path, tuple[str, int]]) -> None:
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    if isinstance(address, tuple):
        site = web.TCPSite(runner, address[0], address[1])
    else:
        site = web.UnixSite(runner, address)
    await site.start()
    print(f"Listening for HTTP connections in {site.name}")
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()
