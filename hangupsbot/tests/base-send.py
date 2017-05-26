"""simple send test
usage: base-send.py [-h] [-i IMAGEPATH] [-n IMAGEFILENAME] url content

positional arguments:
  url                   url to send the data
  content               content to send, quote if it contains spaces

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGEPATH, --imagepath IMAGEPATH
                        image to send as base64-encoded string
  -n IMAGEFILENAME, --imagefilename IMAGEFILENAME
                        image filename

example usage:
python3 base-send.py http://127.0.0.1:9999/<CONV_ID>/ "echo hello world" --imagepath hangoutsbot.png
"""
import argparse, base64

parser = argparse.ArgumentParser()
parser.add_argument("url", help="url to send the data")
parser.add_argument("content", help="content to send, quote if it contains spaces")
parser.add_argument('-i', '--imagepath', help="image to send as base64-encoded string")
parser.add_argument('-n', '--imagefilename', help="image filename")

args = parser.parse_args()

import json
import requests
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

payload = {
    'echo': args.content
}

if args.imagepath:
    with open(args.imagepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    payload["image"] = { "base64encoded": encoded_string.decode('ascii') }
    if args.imagefilename:
        payload["image"]["filename"] = args.imagefilename

headers = {'content-type': 'application/json'}
r = requests.post(args.url, data = json.dumps(payload), headers = headers, verify=False)

print(r)
