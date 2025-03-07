

from gpiozero import Button
from signal import pause

# Initialize buttons with internal pull-up resistors
next_button = Button(13, pull_up=True)  # GPIO 13 (physical pin 33)
prev_button = Button(19, pull_up=True)  # GPIO 19 (physical pin 35)

# Button press handlers
def next_pressed():
    print("Next button pressed")

def prev_pressed():
    print("Previous button pressed")

# Map buttons to handlers
next_button.when_pressed = next_pressed
prev_button.when_pressed = prev_pressed

# Keep the script running
pause()