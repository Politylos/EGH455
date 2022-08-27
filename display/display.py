#!/usr/bin/env python3

# Displays the current IP address and current time to the envrio+ lcd.
# Display updates every 10 seconds

import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont
import logging
#import subprocess
#import socket
from time import sleep, strftime
from datetime import datetime

from get_ip import *

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""display.py - Displays the IP and time on the LCD.""")

# Create LCD class instance.
disp = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display.
disp.begin()

# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height

# New canvas to draw on.
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Text settings.
font_size = 20
font = ImageFont.truetype(UserFont, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

# message = "Hello, World!"


# Keep running.
while True:
    #messageIP = subprocess.check_output(["hostname", "-I"]).split()[0].decode()
    messageIP = get_ip()
    messageDT = datetime.now().strftime("%H:%M")

    # Draw background rectangle and write text.
    draw.rectangle((0, 0, 160, 80), back_colour)
    draw.text((1, 1), "IP Address", font=font, fill=text_colour)
    draw.text((1, 24), messageIP, font=font, fill=text_colour)
    draw.text((1, 48), "Time", font=font, fill=text_colour)
    draw.text((60, 48), messageDT, font=font, fill=text_colour)
    disp.display(img)
    sleep(10)