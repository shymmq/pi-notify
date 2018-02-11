#-*- coding: utf-8 -*-

import websocket
import json
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.virtual import terminal
from PIL import ImageFont,Image
import base64
import unicodedata
import os.path

try:
    import thread
except ImportError:
    import _thread as thread
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#oled setup
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)
font12 = ImageFont.truetype("Tahoma.ttf",12)
font11 = ImageFont.truetype("Tahoma.ttf",11)

subst_chars = {
    'ż':'z',
    'ó':'o',
    'ł':'l',
    'ć':'c',
    'ę':'e',
    'ś':'s',
    'ą':'a',
    'ź':'z',
    'ń':'n'
}

def on_message(ws, raw):

    message = json.loads(raw)
    print(json.dumps(message,indent=4))

    type = message['type']

    if (type == "push"):

        pushdata = message['push']
        pushtype = pushdata['type']

        if(pushtype == 'mirror'):

            package_name = pushdata['package_name']
            app_name = normalize(pushdata['application_name'])
            title =  normalize(pushdata['title'])
            body =  normalize(pushdata['body'])

            icon_path = 'app_icons/'+package_name+'.png'

            if(os.path.isfile(icon_path) ):
                icon = Image.open(icon_path).convert(device.mode)
                device.display(icon)
            else:
                with canvas(device) as draw:
                    w,h = draw.textsize(app_name,font12)
                    draw.text(((device.width-w)/2,(device.height-h)/2), app_name, fill="white",font=font12)
                    pass

            time.sleep(2)

            term = terminal(device,font12,animate=False)

            if (title is not None):
                term.println(title)
                term.font = font11
                term.println('')
                time.sleep(1)

            if (body is not None):
                term.println(body)
                time.sleep(4)

            term.clear()

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def normalize(text):
    for ch,subch in subst_chars.iteritems():
        text = text.replace(ch,subch)
    return text

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.pushbullet.com/websocket/o.xrqhkvkOlwzmiIGdOoAn5FYalM61RCc2",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.run_forever()