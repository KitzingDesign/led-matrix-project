from PIL import Image, ImageFont, ImageDraw
import os
from datetime import datetime

# Define colors
WHITE = (230, 255, 255)

class MainScreen:
    def __init__(self, config, modules):

        # Load the font
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
        font_path = os.path.join(script_dir, "../fonts/Font.otf")  # Adjust path
        self.font = ImageFont.truetype(font_path, 14)



        self.modules = modules
        self.canvas_width = config.getint('System', 'canvas_width', fallback=64)
        self.canvas_height = config.getint('System', 'canvas_height', fallback=32)
        
    def generate(self, inputStatus):
        # Create a black background image
        frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        draw = ImageDraw.Draw(frame)

         # Get the current time and format it as a string
        current_time = datetime.now().strftime("%H:%M")  # Format: HH:MM

         # Text to display (current time)
        text = current_time

        # Get the bounding box of the text
        bbox = self.font.getbbox(text)
        text_width = bbox[2] - bbox[0]  # right - left
        text_height = bbox[3] - bbox[1]  # bottom - top

        # Center the text
        text_x = (self.canvas_width - text_width) / 2
        text_y = (self.canvas_height - text_height) / 2


        # Draw the text
        draw.text((text_x + 1, text_y), text, font=self.font, fill=WHITE)

        return frame  # Return the generated image frame
