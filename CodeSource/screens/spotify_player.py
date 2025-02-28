import numpy as np
from PIL import Image, ImageFont, ImageDraw
import requests
from io import BytesIO
import os
from ast import literal_eval

class SpotifyScreen:
    def __init__(self, config, modules):
        self.modules = modules

        # Load the font
        script_dir = os.path.dirname(os.path.abspath(__file__))  
        font_path = os.path.join(script_dir, "../fonts/Font.otf")  
        self.font = ImageFont.truetype(font_path, 5)
        
        self.canvas_width = config.getint('System', 'canvas_width', fallback=64)
        self.canvas_height = config.getint('System', 'canvas_height', fallback=32)
        self.title_color = literal_eval(config.get('Spotify Player', 'title_color', fallback="(255,255,255)"))
        self.artist_color = literal_eval(config.get('Spotify Player', 'artist_color', fallback="(255,255,255)"))
        self.play_color = literal_eval(config.get('Spotify Player', 'play_color', fallback="(29, 185, 84)"))

        self.current_art_url = ''
        self.current_art_img = None
        self.current_title = ''
        self.current_artist = ''

        self.title_animation_cnt = 0
        self.artist_animation_cnt = 0

        self.is_playing = False

    def generate(self, inputStatus):
        
        spotify_module = self.modules['spotify']
        
        

        response = spotify_module.getCurrentPlayback()
        if response is not None:
            (artist,title,art_url,self.is_playing, progress_ms, duration_ms) = response

            if (self.current_title != title or self.current_artist != artist):
                self.current_artist = artist
                self.current_title = title
                self.title_animation_cnt = 0
                self.artist_animation_cnt = 0
            if self.current_art_url != art_url:
                self.current_art_url = art_url

                response = requests.get(self.current_art_url)
                img = Image.open(BytesIO(response.content))
                self.current_art_img = img.resize((self.canvas_height, self.canvas_height), resample=Image.LANCZOS)

            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)

            draw.line((38,15,58,15), fill=(100,100,100))
            draw.line((38,15,38+round(((progress_ms / duration_ms) * 100) // 5),15), fill=(180,180,180))

            title_len = self.font.getsize(self.current_title)[0]
            if title_len > 31:
                spacer = "   "
                draw.text((34-self.title_animation_cnt, 0), self.current_title + spacer + self.current_title, self.title_color, font = self.font)
                self.title_animation_cnt += 1
                if self.title_animation_cnt == self.font.getsize(self.current_title + spacer)[0]:
                    self.title_animation_cnt = 0
            else:
                draw.text((34-self.title_animation_cnt, 0), self.current_title, self.title_color, font = self.font)

            artist_len = self.font.getsize(self.current_artist)[0]
            if artist_len > 31:
                spacer = "     "
                draw.text((34-self.artist_animation_cnt, 7), self.current_artist + spacer + self.current_artist, self.artist_color, font = self.font)
                self.artist_animation_cnt += 1
                if self.artist_animation_cnt == self.font.getsize(self.current_artist + spacer)[0]:
                    self.artist_animation_cnt = 0
            else:
                draw.text((34-self.artist_animation_cnt, 7), self.current_artist, self.artist_color, font = self.font)

            draw.rectangle((32,0,33,32), fill=(0,0,0))

            if self.current_art_img is not None:
                frame.paste(self.current_art_img, (0,0))

            drawPlayPause(draw, self.is_playing, self.play_color)

            return frame
        else:
            #not active
            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)
            self.current_art_url = ''
            self.is_playing = False
            drawPlayPause(draw, self.is_playing, self.play_color)
            draw.text((0,3), "No Devices", self.title_color, font = self.font)
            draw.text((0,10), "Currently Active", self.title_color, font = self.font)

            return frame

def drawPlayPause(draw, is_playing, color):
    if not is_playing:
        # Draw a play symbol
        draw.line((45, 19, 45, 25), fill=color)
        draw.line((46, 20, 46, 24), fill=color)
        draw.line((47, 20, 47, 24), fill=color)
        draw.line((48, 21, 48, 23), fill=color)
        draw.line((49, 21, 49, 23), fill=color)
        draw.line((50, 22, 50, 22), fill=color)
    else:
        # Draw a pause symbol
        draw.line((45, 19, 45, 25), fill=color)
        draw.line((46, 19, 46, 25), fill=color)
        draw.line((49, 19, 49, 25), fill=color)
        draw.line((50, 19, 50, 25), fill=color)
