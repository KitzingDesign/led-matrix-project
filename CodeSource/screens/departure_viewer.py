import requests
import configparser
import os
import time
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import math

class PublicTransportAPI:
    def __init__(self, config, modules):
        self.modules = modules
        self.config = config

        
        self.last_generate_time = None  # To track when generate was last called

        self.departures = []

        # Load the font
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "../fonts/Font.otf")
        self.font = ImageFont.truetype(font_path, 5)

        # Load the config values
        self.canvas_width = config.getint('System', 'canvas_width', fallback=64)
        self.canvas_height = config.getint('System', 'canvas_height', fallback=32)

        self.border_thickness = 1  # 1-pixel border on all sides
        self.inner_width = self.canvas_width - (2 * self.border_thickness)
        self.inner_height = self.canvas_height - (2 * self.border_thickness)

        self.text_color = (255,165,0)  # Yellow text
    
    
    def generate(self, inputStatus):
        # Calls spotify module to get current playback
        vgr_module = self.modules['VGR']
        gid = 9021014005650000

        current_time = time.time() 

        
        # This if statement is added to prevent the API from being called too often - the api is called every 30 seconds
        
        if self.last_generate_time and (current_time - self.last_generate_time) < 15:
            x=1
              # Skip the generation if not enough time has passed
        else:
            self.departures = vgr_module.get_departures(gid)
            # Update the time of the last generate call
            self.last_generate_time = current_time
        
        

        frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        draw = ImageDraw.Draw(frame)

        if not self.departures:
            text = "No departures found"
            draw.text((self.border_thickness, self.border_thickness), text, self.text_color, font=self.font)
        else:

            line_hight = 0

            current_time = datetime.now(pytz.utc)
            for dep in self.departures:    
                estimated_time_str = dep["estimatedTime"]
                

                if estimated_time_str == "Unknown":
                    minutes_away = "?"
                elif dep["isCancelled"] == True:
                    departure_text = "X"   
                else:
                    try:
                        estimated_time = parser.isoparse(estimated_time_str)
                        minutes_away = math.ceil((estimated_time - current_time).total_seconds() / 60)
                        if minutes_away <= 0:
                            departure_text = "Nu"                       
                        else:
                            departure_text = f"{minutes_away}min"

                    except Exception as e:
                        print(f"Error parsing estimatedTime: {estimated_time_str}, Error: {e}")
                        minutes_away = "?" 

                direction = dep['direction'][:8]

                #Text to display
                
                text = f"{dep['shortName']} {direction}"

                # Get text width
                text_width = self.font.getbbox(departure_text)[2]
                # Calculate right-aligned x position
                x_position = self.canvas_width - text_width 

                
                draw.text((x_position, self.border_thickness + line_hight), departure_text, self.text_color, font=self.font)
                draw.text((self.border_thickness, self.border_thickness + line_hight), text, self.text_color, font=self.font)

                if dep["isCancelled"]:
                    draw.line((self.canvas_width - 10, self.border_thickness + line_hight +2), (255, 0, 0))

                line_hight += 7

        return frame

# Example usage
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('../../config.ini')
    modules = {}  # Add your modules here

    transport_api = PublicTransportAPI(config, modules)

    while True:
        start_time = time.time()  # Track start time
        frame = transport_api.generate(None)
        frame.show()  # Display frame for testing
        
        # Ensure a proper 30-second refresh cycle
        elapsed_time = time.time() - start_time
        sleep_time = max(30 - elapsed_time, 0)  # Avoid negative sleep times
        time.sleep(sleep_time)
