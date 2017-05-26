import aiohttp, asyncio, logging, os, sys, random, urllib.request
import subprocess

from bs4 import BeautifulSoup

import hangups
import plugins

logger = logging.getLogger(__name__)

_externals = { "running": False }

def _initialise(bot):
    plugins.register_user_command(["restart"])
    plugins.register_user_command(["stop"])

def restart(bot, event, *args):
    """Restarts hangoutsbot service on raspberry pi"""

    try:        
        yield from bot.coro_send_message(event.conv.id_, "What are you doing... Dave... Oh, you're restarting. That's cool.")
        subprocess.call(['/bin/systemctl','restart','hangupsbot.service'])

    except Exception as e:
        yield from bot.coro_send_message(event.conv_id, "<i>Issue occurred trying to take or upload photo from camera</i>")
        logger.exception("FAILED TO TAKE/UPLOAD PHOTO")

    finally:
        _externals["running"] = False

def stop(bot, event, *args):
    """Stops hangupsbot"""

    try:        
        yield from bot.coro_send_message(event.conv.id_, "What are you doing... Dave...")
        subprocess.call(['/bin/systemctl','stop','hangupsbot.service'])

    except Exception as e:
        yield from bot.coro_send_message(event.conv_id, "<i>Issue occurred trying to take or upload photo from camera</i>")
        logger.exception("FAILED TO TAKE/UPLOAD PHOTO")

    finally:
        _externals["running"] = False
