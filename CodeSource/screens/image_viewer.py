from PIL import Image, ImageFont, ImageDraw
import os

# Define colors
WHITE = (230, 255, 255)

class ImageViewer:
    def __init__(self, config, modules, default_actions):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script directory
        font_path = os.path.join(script_dir, "../fonts/Font.otf")  # Adjust path
        img_folder = os.path.join(script_dir, "./img")  # Path to image folder

        # 
        try:
            self.font = ImageFont.truetype(font_path, 5)
        except IOError:
            print("Font not found, using default font.")
            self.font = ImageFont.load_default()

        self.modules = modules
        self.default_actions = default_actions
        self.canvas_width = config.getint('System', 'canvas_width', fallback=64)
        self.canvas_height = config.getint('System', 'canvas_height', fallback=32)

        # Load all image file paths from img folder
        self.image_files = [os.path.join(img_folder, f) for f in os.listdir(img_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        self.current_image_index = 0  # Start with first image

    def generate(self, inputStatus):
        # If images are available, display them
        if self.image_files:
            img_path = self.image_files[self.current_image_index]
            try:
                img = Image.open(img_path).convert("RGB")
                
                # Calculate aspect ratio and resize proportionally
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height
                
                # Resize image to fit within canvas while maintaining aspect ratio
                if img_width > img_height:
                    new_width = self.canvas_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = self.canvas_height 
                    new_width = int(new_height * aspect_ratio) 
                
                # Resize the image
                img = img.resize((new_width, new_height), Image.ANTIALIAS)
                
                # Create a black background to center the image
                frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
                # Calculate position to center image
                position = ((self.canvas_width - new_width) // 2, (self.canvas_height - new_height) // 2)
                frame.paste(img, position)

                return frame  # Return the centered and resized image
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")

        # If no images, fallback to text display
        frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        draw = ImageDraw.Draw(frame)

        text = "No images found"
        text_width, text_height = draw.textsize(text, font=self.font)
        text_x = (self.canvas_width - text_width) // 2
        text_y = 2
        draw.text((text_x, text_y), text, font=self.font, fill=WHITE)

        return frame  # Return the generated image frame
