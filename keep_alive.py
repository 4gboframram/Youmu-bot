# This file is used to keep the replit active
# If you're using replit, you can use this.
# To use, use uptimerobot to ping the
# site replit creates every at least 20 minutes

import asyncio
from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/")
async def home(req):
    return web.Response(text="Bot is online")


async def keep_alive():
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    print(f"Listening for HTTP connections in {site.name}")
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()
