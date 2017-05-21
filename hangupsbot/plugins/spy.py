import aiohttp, asyncio, logging, os, sys, random, urllib.request
import subprocess
from PIL import Image
from bs4 import BeautifulSoup

import hangups
import plugins

logger = logging.getLogger(__name__)

_externals = { "running": False }


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

    servo = PanTiltServo()

    try:
        if len(args) == 0 or len(args) > 2    :
            yield from bot.coro_send_message(event.conv_id, "<i>Usage: /bot cam <direction> <amount></i>")
            return

        amount = 200

        if len(args) == 2:
            amount = int(args[1])

        if args[0].lower() == "left":
            servo.look_left(amount)
        if args[0].lower() == "right":
            servo.look_right(amount)
        if args[0].lower() == "up":
            servo.look_up(amount)
        if args[0].lower() == "down":
            servo.look_down(amount)
        if args[0].lower() == "reset":
            servo.reset()

        yield from bot.coro_send_message(event.conv.id_, "Camera moved")

    except Exception as e:
        yield from bot.coro_send_message(event.conv_id, "<i>Issue occurred trying to turn camera</i>")
        logger.exception("FAILED TO TURN CAMERA")

    finally:
        _externals["running"] = False

class Camera:
    name = ""
    path_to_last_photo = ""

    def __init__(self, name="Base"):
        self.name = name

    def take_picture(self, filename):
        self.path_to_last_photo = "/home/pi/Code/hangoutsbot/" + filename

    def upload_last_picture(self, bot, event):
        image_data = open(self.path_to_last_photo,'rb')
        filename = os.path.basename(self.path_to_last_photo)

        logger.debug("uploading {} from {}".format(filename, self.path_to_last_photo))
        
        photo_id = yield from bot._client.upload_image(image_data, filename=filename)
        logger.info("Photo id in method: " + photo_id)
        
        image_data.close
        yield from bot.coro_send_message(event.conv.id_, "File uploaded: ", image_id=photo_id)

class PiCam(Camera):
    def __init__(self, name="PiCam"):
        super(PiCam, self).__init__(name="PiCam")

    #@asyncio.coroutine
    def take_picture(self, filename="picam_image.jpg"):
        subprocess.call(['/usr/bin/raspistill','-t','500','-o',"/home/pi/Code/hangoutsbot/"+filename,'-w','480','-h','600','-q','75','-rot','90','-vf','-hf'])
        #/usr/bin/raspistill -t 0 -s -o /home/pi/Code/hangoutsbot/test.jpg -w 480 -h 600 -q 75 -rot 90 -vf -hf
        super(PiCam, self).take_picture(filename)

class WebCam(Camera):

    def __init__(self, name="WebCam"):
        super(WebCam, self).__init__(name="WebCam")

    #@asyncio.coroutine
    def take_picture(self, filename="webcam_image.jpg"):
        subprocess.call(['/usr/bin/fswebcam','-r','640x480',"/home/pi/Code/hangoutsbot/" + filename])
        super(WebCam, self).take_picture(filename)

class Servo:
    def __init__(self, servo_id=None, default=None, increment=None, min_pos=500, max_pos=2500):
        if max_pos is None:
            max_pos = 2500
        if min_pos is None:
            min_pos = 500
        if default is None:
            default = 1500
        if servo_id is None:
            servo_id = 0
        if increment is None:
            increment = 200

        self._servo_id = servo_id
        self._default = default
        self._increment = increment
        self._min = min_pos
        self._max = max_pos

    def set_increment(self, amount=None):
        if amount is None:
            amount = self._increment

        self.validate(abs(amount))

        symbol = "+"

        if amount < 0:
            symbol = "-"

        with open('/dev/servoblaster', 'w') as f:
            f.write(str(self._servo_id) + "=" + symbol + str(abs(amount)) + "us\n")

    def reset(self):
        with open('/dev/servoblaster', 'w') as f:
            f.write(str(self._servo_id) + "=" + str(self._default) + "us\n")

    def validate(self, increment):
        if increment > self._max:
            raise ValueError("Position is invalid. Given: " + str(self._increment) + ", Min: " + str(self._min) + ", Max: " + str(self._max))


class PanTiltServo:
    def __init__(self):
        self._leftright = Servo(0,1500,200)
        self._updown = Servo(1,600,100)

    def look_left(self,amount):
        self._leftright.set_increment(-amount)

    def look_right(self,amount):
        self._leftright.set_increment(amount)

    def look_down(self,amount):
        self._updown.set_increment(-amount)

    def look_up(self,amount):
        self._updown.set_increment(amount)

    def reset(self):
        self._leftright.reset()
        self._updown.reset()


class AllCams(Camera):
    _picam = PiCam()
    _webcam = WebCam()

    def __init__(self, name="AllCams"):
        super(AllCams, self).__init__(name="AllCams")

    def take_picture(self):
        self._picam.take_picture()
        self._webcam.take_picture()

    def upload_last_picture(self, bot, event):
        yield from self._picam.upload_last_picture(bot, event)
        yield from self._webcam.upload_last_picture(bot, event)