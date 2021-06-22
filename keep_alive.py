# This file is used to keep the replit active
# If you're using replit, you can use this.
# To use, use uptimerobot to ping the
# site replit creates every at least 20 minutes

import asyncio
from aiohttp import web
import typing
import pathlib
from contextlib import asynccontextmanager

routes = web.RouteTableDef()


@routes.get("/")
async def home(req):
    return web.Response(text="Bot is online")


@asynccontextmanager
async def Runner(runner: web.BaseRunner):
    await runner.setup()
    try:
        yield runner
    finally:
        await runner.cleanup()


async def keep_alive(address: typing.Union[pathlib.Path, tuple[str, int], None]) -> None:
    app = web.Application()
    app.add_routes(routes)
    async with Runner(web.AppRunner(app)) as runner:
        if isinstance(address, tuple):
            site = web.TCPSite(runner, address[0], int(address[1]))
        else:
            site = web.UnixSite(runner, str(address))
        await site.start()
        print(f"Listening for HTTP connections in {site.name}")
        while True:
            await asyncio.sleep(3600)
    