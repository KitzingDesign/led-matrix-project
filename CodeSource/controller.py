import queue
import math, sys, os, time, copy, inspect
from InputStatus import InputStatusEnum

# Tries to import button from module, if not working it defines its own placeholders
try:
    from gpiozero import Button
except:
    class Button:
        def __init__(self, num, pull_up=False):
            self.num = num
            self.pull_up = pull_up
            self.when_pressed = lambda : None

import configparser
from PIL import Image
import select

from screens import main_screen, gif_viewer, image_viewer, spotify_player, departure_viewer
from modules import spotify_module, vgr_module

# Set up GPIO and the display options
prev_button_pin = 13  # GPIO 13 (physical pin 33)
next_button_pin = 19  # GPIO 19 (physical pin 35)

def main():
    brightness = 100
    displayOn = True

    # Get the absolute path of the config file
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    config_file_path = os.path.join(script_dir, '../config.ini')  # Build the path to config.ini

    # This code imports the values from the config file
    config = configparser.ConfigParser()
    parsed_configs = config.read(config_file_path)
    if len(parsed_configs) == 0:
        print("no config file found")
        sys.exit()

    # Sets the width/height of the screen, can be set in config file, otherwise fallback w=64, h=32
    canvas_width = config.getint('System', 'canvas_width', fallback=64)
    canvas_height = config.getint('System', 'canvas_height', fallback=32)

    # Sets background image to black
    black_screen = Image.new("RGB", (canvas_width, canvas_height), (0,0,0))

    # Sets what the button will do
    prevButton = Button(prev_button_pin, pull_up=True)  # Previous button
    nextButton = Button(next_button_pin, pull_up=True)  # Next button

    inputStatusDict = {"value" : InputStatusEnum.NOTHING}

    # Turns the display on and off
    def toggle_display():
        nonlocal displayOn
        displayOn = not displayOn
        print("Display On: " + str(displayOn))

    # Increase brightness
    def increase_brightness():
        nonlocal brightness
        brightness = min(100, brightness + 5)

    # Decrease Brightness
    def decrease_brightness():
        nonlocal brightness
        brightness = max(0, brightness - 5)

    # Changes which app is visible
    current_app_idx = 0
    def switch_next_app():
        nonlocal current_app_idx
        current_app_idx = (current_app_idx + 1) % len(app_list)  # Cycle forward
        print(f"Next button pressed. Switched to app: {app_list[current_app_idx].__class__.__name__}")

    def switch_prev_app():
        nonlocal current_app_idx
        current_app_idx = (current_app_idx - 1) % len(app_list)  # Cycle backward
        print(f"Previous button pressed. Switched to app: {app_list[current_app_idx].__class__.__name__}")

    callbacks = {
                    'toggle_display' : toggle_display,
                    'increase_brightness' : increase_brightness,
                    'decrease_brightness' : decrease_brightness,
                    'switch_next_app' : switch_next_app,
                    'switch_prev_app' : switch_prev_app
                }
    
    modules = {'spotify' : spotify_module.SpotifyModule(config), 'VGR': vgr_module.VGRModule(config) }

    # All screens 
    app_list = [main_screen.MainScreen(config, modules), departure_viewer.PublicTransportAPI(config, modules),  spotify_player.SpotifyScreen(config, modules)]

    # Map "next" and "prev" buttons to the corresponding functions
    nextButton.when_pressed = lambda: callbacks['switch_next_app']()
    prevButton.when_pressed = lambda: callbacks['switch_prev_app']()

    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir+"/rpi-rgb-led-matrix/bindings/python")

    # Importing rgbmatrix for python 
    try:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions
    except ImportError:
        from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

    # Initialize a new options object for rgb matrix
    options = RGBMatrixOptions()
    options.rows = canvas_height
    options.cols = canvas_width
    options.chain_length = 1
    options.parallel = 1
    options.brightness = brightness
    options.gpio_slowdown = 4
    options.pwm_lsb_nanoseconds = 80
    options.limit_refresh_rate_hz = 150
    options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
    options.drop_privileges = False
    matrix = RGBMatrix(options=options)

    while(True):
        inputStatusSnapshot = copy.copy(inputStatusDict['value'])
        inputStatusDict['value'] = InputStatusEnum.NOTHING

        frame = app_list[current_app_idx % len(app_list)].generate(inputStatusSnapshot)
        if not displayOn:
            frame = black_screen
        
        matrix.SetImage(frame)
        time.sleep(0.05)

def encButtonFunc(enc_button, inputStatusDict):
    start_time = time.time()
    time_diff = 0
    hold_time = 1

    while enc_button.is_active and (time_diff < hold_time):
        time_diff = time.time() - start_time

    if (time_diff >= hold_time):
        print("long press detected")
        inputStatusDict['value'] = InputStatusEnum.LONG_PRESS
    else:
        enc_button.when_pressed = None
        start_time = time.time()
        while (time.time() - start_time <= 0.3):
            time.sleep(0.1)
            if (enc_button.is_pressed):
                time.sleep(0.1)
                new_start_time = time.time()
                while (time.time() - new_start_time <= 0.3):
                    time.sleep(0.1)
                    if (enc_button.is_pressed):
                        print("triple press detected")
                        inputStatusDict['value'] = InputStatusEnum.TRIPLE_PRESS
                        enc_button.when_pressed = lambda button : encButtonFunc(button, inputStatusDict)
                        return
                print("double press detected")
                inputStatusDict['value'] = InputStatusEnum.DOUBLE_PRESS
                enc_button.when_pressed = lambda button : encButtonFunc(button, inputStatusDict)
                return
        print("single press detected")
        inputStatusDict['value'] = InputStatusEnum.SINGLE_PRESS
        enc_button.when_pressed = lambda button : encButtonFunc(button, inputStatusDict)
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted with Ctrl-C')
        sys.exit(0)