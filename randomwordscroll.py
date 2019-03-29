#!/usr/bin/env python3
import os
import sys
import time
import signal
import json

from luma.core.render import canvas
from PIL import ImageFont
from randomwordgenerator import randomwordgenerator

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106

from threading import Thread
import time
import random



# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)
Width=128
Height=64
font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts",'cour.ttf'))
#print(font_path)
courfont = ImageFont.truetype(font_path, 36)
smallfont = ImageFont.truetype(font_path, 20)
reallysmallfont = ImageFont.truetype(font_path, 16)
font=courfont
scrollspeed=4

text_file = open("words_alpha.txt", "r")
lines = text_file.read().split("\n")


class Scrollthread(Thread):
    def __init__(self, word):
        Thread.__init__(self)
        self.word=word
        self.end=False
        self.Width=Width
        with canvas(device) as draw:
            self.w,self.h = draw.textsize(self.word,font=font)

    def run(self):  ##scroll
        #print("scrolling",self.word)

        x=Width
        while True:
            x,word = wordDisplay(x,self.word)
            if(x<-(self.w-2)):
                break
            if(x<-(self.w-10)):
                self.end=True

        self.end=True


def wordDisplay(count,word):
    with canvas(device) as draw:
        w,h = draw.textsize(word,font=font)
        if(count<-(w-2)):
            count=0
            return

        draw.text((count, (Height/2)-(h/2)), word, font=font, fill="white")
        #draw.text((count+(w+5), 50), lines[230], font=reallysmallfont, fill="white")
        count-=scrollspeed
    return count,word





if __name__ == "__main__":
    try:
        #word=randomwordgenerator.generate_random_words(1)
        x=Width

        #word=randomwordgenerator.generate_random_words(1)
        word=lines[random.randint(0,len(lines))]
        while True:

            lastword=word
            scrollthread = Scrollthread(word=word)  ##
            scrollthread.start()                ###start a scroll
            #x,word = wordDisplay(x,word)




            while(scrollthread.end==False):
                if(word==lastword):
                    word=lines[random.randint(0,len(lines))]
                    #word=randomwordgenerator.generate_random_words(1)
                    #print("get new word ",word, "while waiting")
                #print("waiting")
                time.sleep(.5)




    except KeyboardInterrupt:
        pass
