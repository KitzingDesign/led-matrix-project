from PIL import Image, ImageFont, ImageDraw
import os

# Define colors
WHITE = (230, 255, 255)

class MainScreen:
    def __init__(self, config, modules, default_actions):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
        font_path = os.path.join(script_dir, "../fonts/Font.otf")  # Adjust path

        # Load font (fallback if not found)
        try:
            self.font = ImageFont.truetype(font_path, 5)
        except IOError:
            print("Font not found, using default font.")
            self.font = ImageFont.load_default()

        self.modules = modules
        self.default_actions = default_actions
        self.canvas_width = config.getint('System', 'canvas_width', fallback=64)
        self.canvas_height = config.getint('System', 'canvas_height', fallback=32)
        
        self.selectMode = False

    def generate(self, inputStatus):
        # Create a black background image
        frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        draw = ImageDraw.Draw(frame)

        # Text to display
        text = "0725766707"
        text_width, text_height = draw.textsize(text, font=self.font)

        # Center the text
        text_x = (self.canvas_width - text_width) // 2
        text_y = 2

        # Draw the text
        draw.text((text_x, text_y), text, font=self.font, fill=WHITE)

        return frame  # Return the generated image frame
