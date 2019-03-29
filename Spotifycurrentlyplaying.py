#!/usr/bin/env python3
import os
import sys
import time
import signal
import json
import spotipy
import spotipy.util as util
import time
import json

from luma.core.render import canvas
from PIL import ImageFont
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1309, ssd1325, ssd1331, sh1106
from threading import Thread
from json.decoder import JSONDecodeError
from datetime import datetime
from datetime import timedelta


font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts",'cour.ttf'))
#

font = ImageFont.truetype(font_path, 18)

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)
Width=128
Height=64

scrollspeed=2
songfontsize=20
artistfontsize=15


###fill these in from spotify api
client_id =
client_secret =
redirect_uri =

username =
scope = 'user-read-playback-state'


class Spotify:
    def __init__(self, username, scope, client_id, client_secret, redirect_uri):
        self.username = username
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        try:
            self.token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)


        except (AttributeError, JSONDecodeError):
            os.remove(".cache-{}".format(username))
            self.token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)


    def reload(self):
        if self.token:
            sp = spotipy.Spotify(auth=self.token)
            playback = sp.current_playback()


            try:
                self.track = playback['item']['name']
                self.artist = playback['item']['artists'][0]['name']
                self.durationMs = playback['item']['duration_ms']
                self.progressMs = playback['progress_ms']
                self.shuffleState = playback['shuffle_state']
                self.isPlaying = playback['is_playing']
            except TypeError:
                print("nothing playing")
        else:
            print("Unable to retrieve current playback - Can't get token for ", username)

    def __str__(self):
        return "playing "+self.track+" by "+self.artist+"from Spotify"



class Scrollthread(Thread):
    def __init__(self, word,scrolling,fontsize,ypos):
        Thread.__init__(self)
        self.word=word
        self.end=False
        self.Width=Width
        self.x=5
        self.scrolling=scrolling
        self.ypos=ypos
        self.font = ImageFont.truetype(font_path, fontsize)
        self.move=False          ##true=right
        #print("fonted")
        with canvas(device) as draw:
            self.w,self.h = draw.textsize(self.word,font=self.font)

    def run(self):  ##scroll
        #print("scrolling",self.word)

        while True:
            lastmove =self.move
            if(self.scrolling and self.end==False):                     ###This could be cleaner by only using one while loop and a reverse variable

                if(self.move):
                    self.x += scrollspeed*4
                else:
                    self.x -= scrollspeed



                if (self.x < ((Width-self.w)-10) and self.move==False):      #was moving left and has moved enough
                    self.move=True


                else:
                    if((self.x>0 and self.move==True)):                     #was moving right and more than 0
                        self.move=False


                if(self.move==False and lastmove==True):
                    self.end=True
                    time.sleep(3)
            time.sleep(.2)



    def drawobj(self):
            draw.text((self.x, self.ypos), self.word, font=self.font, fill="white")
            #print("drawn at",self.x,self.ypos)



class Seekthread(Thread):
    def __init__(self,currentpos,songlen,isplaying):
        Thread.__init__(self)
        self.padding=5
        self.currentpos=currentpos
        self.lasttime=int(time.time())
        self.songlen=songlen
        self.end=False
        self.isplaying=isplaying

    def run(self):
        while True:

            diff=time.time()-self.lasttime
            self.lasttime=time.time()
            self.currentpos+=diff
            percent=self.currentpos/self.songlen
            #print(int(percent*100),"%")
            self.xpos=int((percent)*(Width-self.padding*2))
            if(percent>=1):
                self.end=True
            time.sleep(.3)

    def setcurrentpos(self,currentpos):
        self.currentpos=currentpos

    def drawobj(self):
        if(self.isplaying):
            draw.rectangle((5, (Height - 6), (Width - 5), (Height - 2)), "black", "white",1)  ###scroll bar 6 high with 5 xpadding and 2 bottom padding
            ##10 high * 4 wide
            draw.rectangle((self.xpos - 2, (Height - 10), (self.xpos + 2), (Height)), "black", "white", 2)
        else:
            ####draw pause
            draw.rectangle((66, (Height - 14), (70), (Height)), "black", "white", 2)
            draw.rectangle((54, (Height - 14), (58), (Height)), "black", "white", 2)




if __name__ == "__main__":
    try:
        with canvas(device) as draw:
            draw.text((50, 32), "loading", font=ImageFont.truetype(font_path, 12), fill="white")
        spotifyobj = Spotify(username=username,scope=scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)
        lastsong=""
        spotifyobj.reload()
        reloadnum=0
        networktimeout=1                   ##ten seconds
        justdrawtime = datetime.now() + timedelta(seconds=networktimeout)
        while True:

            if reloadnum>30:
                spotifyobj = Spotify(username=username, scope=scope, client_id=client_id, client_secret=client_secret,redirect_uri=redirect_uri)
                spotifyobj.reload()
                reloadnum=0
            try:
                playing = spotifyobj.isPlaying
                lastsong=spotifyobj.track+spotifyobj.artist
            except AttributeError:
                pass
            print(spotifyobj)




            with canvas(device) as draw:
                w, h = draw.textsize(spotifyobj.track, font=ImageFont.truetype(font_path, songfontsize))
            if(w>Width):
                songscrollthread = Scrollthread(word=spotifyobj.track,scrolling=True,fontsize=songfontsize,ypos=5)
                print("with scrolling")
            else:
                songscrollthread = Scrollthread(word=spotifyobj.track, scrolling=False,fontsize=songfontsize,ypos=5)
            songscrollthread.start()


            with canvas(device) as draw:
                w, h = draw.textsize(spotifyobj.artist, font=ImageFont.truetype(font_path, songfontsize))
            if(w>Width):
                artistscrollthread = Scrollthread(word=spotifyobj.artist,scrolling=True,fontsize=artistfontsize,ypos=30)
            else:
                artistscrollthread = Scrollthread(word=spotifyobj.artist, scrolling=False,fontsize=artistfontsize,ypos=30)
            artistscrollthread.start()

            with canvas(device) as draw:
                songscrollthread.drawobj()
                artistscrollthread.drawobj()


            seekthread = Seekthread((spotifyobj.progressMs / 1000), (spotifyobj.durationMs / 1000), isplaying=playing)
            seekthread.start()


            while seekthread.end==False:                            ###while song is still playing. This could be while true with seekthread.end as an interrupt

                with canvas(device) as draw:
                    songscrollthread.drawobj()
                    artistscrollthread.drawobj()
                    seekthread.drawobj()

                if(datetime.now()>justdrawtime):

                    if(songscrollthread.scrolling==False):      ###potentitally should check if both are not scrolling
                        print("checking song")
                        spotifyobj.reload()
                        reloadnum += 1
                        seekthread.currentpos=spotifyobj.progressMs/1000
                        seekthread.isplaying=spotifyobj.isPlaying
                        justdrawtime = datetime.now() + timedelta(seconds=networktimeout)

                        if(spotifyobj.track+spotifyobj.artist!=lastsong):
                            break
                        else:
                            artistscrollthread.end = False



                    else:
                        #print("songscroll.end",songscrollthread.end,"songscroll.x",songscrollthread.x,"move",songscrollthread.move)
                        if(songscrollthread.end):           ###potentially should check if both scrolls are at 0 but
                            print("scroll ended, checking song")
                            spotifyobj.reload()
                            reloadnum+=1
                            seekthread.currentpos = spotifyobj.progressMs / 1000
                            seekthread.isplaying = spotifyobj.isPlaying
                            if (spotifyobj.track + spotifyobj.artist != lastsong):
                                print("diff song")
                                break
                            else:
                                #songscrollthread.x=0
                                songscrollthread.end=False
                                artistscrollthread.end = False
                                justdrawtime = datetime.now() + timedelta(seconds=networktimeout)
                else:
                    pass
                    #print("only drawing")

            spotifyobj.reload()

            reloadnum += 1
            print("song ended or changed")

    except KeyboardInterrupt:
        pass
