import aiohttp, asyncio, logging, os, sys, random, urllib.request
import subprocess
from .servo import Servo
from .servo import PanTiltServo
from .cam import *

from PIL import Image
from bs4 import BeautifulSoup

import hangups
import plugins

logger = logging.getLogger(__name__)

_externals = { "running": False }
_servo = PanTiltServo(PiCam(),leftright_increment=75,updown_increment=25)

def _initialise(bot):
    plugins.register_user_command(["spy"])
    plugins.register_user_command(["cam"])

def spy(bot, event, *args):
    """Searches for a meme related to <something>;
    grabs a random meme when none provided"""

    cam = AllCams()

    image_data = ""

    try:        
        if len(args) > 0:
            if args[0] == "0":
                cam = PiCam()
            elif args[0] == "1":
                cam = WebCam()

        cam.take_picture()
        yield from cam.upload_last_picture(bot, event)

    except Exception as e:
        yield from bot.coro_send_message(event.conv_id, "<i>Issue occurred trying to take or upload photo from camera</i>")
        logger.exception("FAILED TO TAKE/UPLOAD PHOTO")

    finally:
        _externals["running"] = False

def cam(bot, event, *args):
    """Searches for a meme related to <something>;
    grabs a random meme when none provided"""

    try:
        if len(args) == 0 or len(args) > 3:
            yield from bot.coro_send_message(event.conv_id, "<i>Usage: /bot cam <direction> <amount></i>")
            return

        if len(args) == 2:
            amount = int(args[1])
        else:
            amount = None

        command = args[0].lower()
        take_photo_after = True

        if command == "left":
            _servo.look_left(amount)
        if command == "right":
            _servo.look_right(amount)
        if command == "up":
            _servo.look_up(amount)
        if command == "down":
            _servo.look_down(amount)
        if command == "reset":
            _servo.reset()
        if command == "rotate":
            _servo._camera.set_rotation(args[1])
        if command == "pos":
            yield from bot.coro_send_message(event.conv.id_, "Camera orientation: {0}, {1}".format(_servo._leftright._curpos,_servo._updown._curpos))
        if command == "save":
            take_photo_after = False
            if len(args) == 3:
                _servo._leftright._default = args[1]
                _servo._updown._default = args[2]
                _servo.reset()
            else:
                _servo.save()

            yield from bot.coro_send_message(event.conv.id_, "Default position set to {0}, {1}".format(_servo._leftright._default,_servo._updown._default))
        if command == "set":
            if len(args) == 3:
                _servo.moveto(int(args[1]), int(args[2]))
        if command == "enhance":
            take_photo_after = False
            _servo._camera.take_picture(enhance=True)
            yield from bot.coro_send_message(event.conv.id_, "Enhancement levels: {0}".format(_servo._camera.enhance_counter))

        if take_photo_after is True:
            _servo._camera.take_picture()

        yield from _servo._camera.upload_last_picture(bot, event)

        yield from bot.coro_send_message(event.conv.id_, "")

    except Exception as e:
        yield from bot.coro_send_message(event.conv_id, "<i>Issue occurred trying to turn camera</i>")
        logger.exception("FAILED TO TURN CAMERA")

    finally:
        _externals["running"] = False
