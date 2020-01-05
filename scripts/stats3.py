# -*- coding: utf-8 -*-

"""
Adapted from an example from adafruit.com

This is a slightly optimized version where the cpu load
is greatly reduced. This is done by redrawing the display
only when there are changes. The cpu load reduced from 100%
to less than 4% (basically it does nothing when no change).
"""

import time
from collections import defaultdict

import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789



# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE,
                     width=135, height=240, x_offset=53, y_offset=40)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width   # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new('RGB', (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

output_dict = defaultdict(str)

draw_count = 0
while True:
    # Draw a black filled box to clear the image.
    if draw_count > 0:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = "IP: "+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'" # pylint: disable=line-too-long
    Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # # Write four lines of text.

    draw_count = 0 # number of drawing commands used
    y = top
    if IP != output_dict['IP']:
        output_dict['IP'] = IP
        draw.text((x, y), IP, font=font, fill="#FFFFFF")
        draw_count += 1
    y += font.getsize(IP)[1]
    if CPU != output_dict['CPU']:
        output_dict['CPU'] = CPU
        draw.text((x, y), CPU, font=font, fill="#FFFF00")
        draw_count += 1
    y += font.getsize(CPU)[1]
    if MemUsage != output_dict['MemUsage']:
        output_dict['MemUsage'] = MemUsage
        draw.text((x, y), MemUsage, font=font, fill="#00FF00")
        draw_count += 1
    y += font.getsize(MemUsage)[1]
    if Disk != output_dict['Disk']:
        output_dict['Disk'] = Disk
        draw.text((x, y), Disk, font=font, fill="#0000FF")
        draw_count += 1
    y += font.getsize(Disk)[1]
    if Temp != output_dict['Temp']:
        output_dict['Temp'] = Temp
        draw.text((x, y), Temp, font=font, fill="#FF00FF")
        draw_count += 1

    # Display image.
    if draw_count > 0:
        disp.image(image, rotation)
        print(draw_count)
    time.sleep(0.1)

