#!/usr/bin/env python3
import os
import sys
import time
import signal
import json

from luma.core.render import canvas
from PIL import ImageFont


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
courfont = ImageFont.truetype(font_path, 30)
smallfont = ImageFont.truetype(font_path, 20)
reallysmallfont = ImageFont.truetype(font_path, 16)
font = ImageFont.truetype(font_path, 5)
scrollspeed=4

text_file = open("words_alpha.txt", "r")
lines = text_file.read().split("\n")

fontsize=5

class Showword(Thread):
    def __init__(self, word):
        Thread.__init__(self)
        self.word=word
        self.end=False

    def run(self):  ##scroll
        if(len(word)>=16):
                fontsize=12
                font= ImageFont.truetype(font_path, fontsize)
        else:
            if(len(word)>=11):
                fontsize=14
                font=ImageFont.truetype(font_path,fontsize)
            else:
                if(len(word)>=9):
                    fontsize=18
                    font=ImageFont.truetype(font_path, fontsize)
                else:
                    if(len(word)>=7):
                        fontsize=20
                        font=ImageFont.truetype(font_path, fontsize)
                    else:
                        if(len(word)>=5):
                            fontsize=32
                            font=ImageFont.truetype(font_path, fontsize)
                        else:
                            fontsize=48
                            font=ImageFont.truetype(font_path, fontsize)

        #print("scrolling",self.word)
        x=Width
        with canvas(device) as draw:
            w,h = draw.textsize(self.word,font=font)

            draw.text(((Width/2)-(w/2), (Height/2)-(h/2)), self.word, font=font, fill="white")

            self.end=True


def wordDisplay(count,word):
    with canvas(device) as draw:
        w,h = draw.textsize(word,font=font)
        if(count<-(w-2)):
            count=Width
        draw.text((count, (Height/2)-(h/2)), word, font=font, fill="white")
        draw.text((56,60),)
    count-=scrollspeed
    return count,word





if __name__ == "__main__":
    try:


        x=Width

        word=lines[random.randint(0,len(lines))]
        font=courfont
        while True:
            lastword=word
            showword = Showword(word=word)  ##
            showword.start()                ###start a scroll
            #x,word = wordDisplay(x,word)
            #print("get new word")



            while(showword.end==False):
                if(word==lastword):

                    word=lines[random.randint(0,len(lines))]

            time.sleep(.1)


    except KeyboardInterrupt:
        pass
