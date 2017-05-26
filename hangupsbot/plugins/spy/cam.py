import os, sys, asyncio, logging, subprocess, math
import time
from picamera import PiCamera

DEFAULT_RESOLUTION = (800,600)
HIGH_RESOLUTION = (1024,768)

class Camera:
    name = ""
    path_to_last_photo = ""
    logger = logging.getLogger(__name__)
    image_output_path = ""

    def __init__(self,name="Base",rotation=None,orientation=None):
        self.name = name
        self.image_output_path = "/home/pi/Code/hangoutsbot/"
        self.rotation = rotation
        self.orientation = orientation

    def take_picture(self, filename):
        self.path_to_last_photo = self.get_image_filepath(filename)

    def upload_last_picture(self, bot, event):
        image_data = open(self.path_to_last_photo,'rb')
        filename = os.path.basename(self.path_to_last_photo)

        self.logger.debug("uploading {} from {}".format(filename, self.path_to_last_photo))
        
        photo_id = yield from bot._client.upload_image(image_data, filename=filename)
        self.logger.info("Photo id in method: " + photo_id)
        
        image_data.close
        yield from bot.coro_send_message(event.conv.id_, "", image_id=photo_id)

    def get_image_filepath(self,filename):
        return "{0}/{1}".format(self.image_output_path,filename)

    def enhance(self):
        return

class PiCam(Camera):
    enhance_counter = 0

    def __init__(self, name="PiCam"):
        super(PiCam, self).__init__(name="PiCam",rotation=90,orientation="w")

    #@asyncio.coroutine
    def take_picture(self, filename="picam_image.jpg", enhance=False):
        with PiCamera(resolution=DEFAULT_RESOLUTION) as cam_api:
            cam_api.rotation = self.rotation
            cam_api.vflip = True
            cam_api.hflip = True

            if enhance is True:
                self.enhance_counter = self.enhance_counter + 1
                cam_api.resolution = HIGH_RESOLUTION
                enhance_factor = 1/(math.pow(2, self.enhance_counter))
                cam_api.zoom = (0.0,0.0,enhance_factor,enhance_factor)
                #cam_api.zoom = (cam_api.resolution.width/2,cam_api.resolution.height/2,enhance_factor,enhance_factor)
            else:
                self.enhance_counter = 0
                cam_api.resolution = DEFAULT_RESOLUTION

            cam_api.capture(self.get_image_filepath(filename))
        super(PiCam, self).take_picture(filename)

    def set_rotation(self, rotation):
        self.rotation = rotation

class WebCam(Camera):
    def __init__(self, name="WebCam"):
        super(WebCam, self).__init__(name="WebCam")

    #@asyncio.coroutine
    def take_picture(self, filename="webcam_image.jpg"):
        subprocess.call(['/usr/bin/fswebcam','-r','640x480',self.get_image_filepath(filename)])
        super(WebCam, self).take_picture(filename)

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