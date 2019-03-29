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

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)
Width=128
Height=64
#font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts', 'C&C Red Alert [INET].ttf'))
font = ImageFont.truetype("cour.ttf", 30)
smallfont = ImageFont.truetype('cour.ttf', 18)
reallysmallfont = ImageFont.truetype('cour.ttf', 13)





def sentenceticker(index,sentence):
    end=False
    if(index>len(sentence.split())-1):
        with canvas(device) as draw:
            draw.rectangle((51,27,5,5),fill="white");
            time.sleep(.1)
        end=True
        index=0

    word=sentence.split()[index]

    with canvas(device) as draw:
        if(len(word)>10):
            w,h = draw.textsize(word,font=reallysmallfont)
            draw.text(((Width/2)-(w/2),(Height/2)-(h/2)),word,font=reallysmallfont,fill="white")

        else:
            if(len(word)>6):
                w,h = draw.textsize(word,font=smallfont)
                draw.text(((Width/2)-(w/2),(Height/2)-(h/2)),word,font=smallfont,fill="white")
            else:
                w,h = draw.textsize(word,font=font)
                draw.text(((Width/2)-(w/2),(Height/2)-(h/2)),word,font=font,fill="white")
        index+=1

    return index,end


if __name__ == "__main__":
    try:


        sentenceindex=0
        starttime=time.time()
        headlineindex=0
        headlines=[]
        headlines.append("What do voters make of Brexit now?")
        headlines.append("Breast ironing awareness 'needed in school'")
        headlines.append("England players condemn racist abuse")
        headlines.append("MPs 'seize control of Brexit'")
        headlines.append("Stormy Daniels lawyer accused of extortion")
        headlines.append("UK urged to guarantee EU citizens' benefits")
        headlines.append("Apple unveils TV streaming platform")
        headlines.append("Joe Lycett calls for better LGBT dialogue")
        headlines.append("'I paid £160 for a pair of limited edition nappies'")




        while True:
            #artistcount,word = artistdisplay(artistcount,word)
            sentence = headlines[headlineindex]
            sentenceindex,end = sentenceticker(sentenceindex,sentence)
            if(end):
                headlineindex+=1
                #get new sentence

            if(headlineindex==len(headlines)):
                headlineindex=0
            time.sleep(.2)



    except KeyboardInterrupt:
        pass
