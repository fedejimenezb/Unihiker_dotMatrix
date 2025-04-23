UniHiker Dot Matrix Display Library Documentation
This document describes how to use the DotMatrixDisplay Python library to create an animated dot matrix effect on a UniHiker screen. The library allows you to display predefined shapes using blocks of flickering dots, with different brightness levels for highlighted and background blocks.

1. Setup

Save the Library: Save the Python code containing the DotMatrixDisplay class and its helper classes (_Dot, _Block) as a Python file (e.g., dot_matrix_lib.py) on your UniHiker device.

UniHiker Library: Ensure the standard UniHiker Python library is installed and working on your device, as this library depends on it (from unihiker import GUI).

2. Basic Usage

Here's a simple example of how to import and use the library in your own Python script:

# main_program.py
import time
from dot_matrix_lib import DotMatrixDisplay # Assuming you saved the library as dot_matrix_lib.py

# --- Optional: Define custom configuration ---
# You can override any default settings here
my_config = {
    "dot_size": 10,
    "animation_interval": 0.05,
    "update_percentage_high": 0.3,
    "update_percentage_low": 0.1,
    "show_ids": False
}

# --- Create an instance of the display ---
# display = DotMatrixDisplay() # Use all default settings
display = DotMatrixDisplay(config=my_config) # Use custom settings

# --- Run the continuous animation ---
# The run_continuous method handles the animation loop internally.
# You can specify the initial shape to display.
try:
    display.run_continuous(initial_shape="cross")
except KeyboardInterrupt:
    print("Program interrupted by user.")
# The cleanup method is called automatically within run_continuous's finally block.

print("Main program finished.")

3. DotMatrixDisplay Class

This is the main class you interact with.

Initialization:

display = DotMatrixDisplay(config=None)

config (dict, optional): A dictionary containing configuration values to override the defaults (see Section 4). If omitted, DEFAULT_CONFIG is used.

Public Methods:

set_target_shape(shape_name):

Sets the currently active shape to be highlighted. Blocks belonging to this shape will use the "high" brightness settings, while others use the "low" settings.

Args:

shape_name (str): The name of the shape (must be a key in the config["shapes"] dictionary). Use "none" to turn off all highlighting.

It also handles redrawing blocks that change from high to low brightness immediately for a cleaner transition.

update_frame():

Updates a single frame of the animation. It selects a random percentage of dots within both high and low brightness blocks and redraws them with a random brightness within their respective ranges.

You would call this repeatedly in your own custom animation loop if you are not using run_continuous().

run_continuous(initial_shape="circle"):

Starts and manages the continuous animation loop using a non-blocking delay (time.monotonic()). It repeatedly calls update_frame() based on the animation_interval.

It also prints the frame count, timestamp, and current shape name to the console periodically.

The loop runs until interrupted by Ctrl+C.

Args:

initial_shape (str, optional): The name of the shape to display when the animation starts. Defaults to "circle".

Includes a finally block to call cleanup() automatically on exit.

cleanup():

Attempts to clear the UniHiker screen by drawing a black rectangle over the entire display area. Called automatically by run_continuous() when it exits. You might call this manually if you manage your own loop and want to clear the screen upon stopping.

4. Configuration Options

You can customize the display's behavior by passing a config dictionary during instantiation. Any values you provide will override the defaults. Here are the available options in DEFAULT_CONFIG:

dot_size (int): Pixel size (width and height) of each displayed dot. Default: 12.

dot_spacing (int): Internal spacing used for layout calculations based on the original 6x6 grid concept. Default: 6.

bg_color (str): Background color string (e.g., 'black', '#000000'). Default: 'black'.

block_size (int): The conceptual grid size within a block used for layout calculations. Default: 6.

block_gap_dots (int): The gap between blocks, measured in original dot spacing units. Default: 2.

super_dot_offset (int): Pixel offset from the block's center used to position the 4 dots. Default: 8.

animation_interval (float): Target time in seconds between frame updates. Default: 0.02.

update_percentage_high (float): Fraction (0.0 to 1.0) of dots in high-brightness blocks to update each frame. Default: 0.25.

update_percentage_low (float): Fraction (0.0 to 1.0) of dots in low-brightness blocks to update each frame. Default: 0.05.

shapes (dict): A dictionary where keys are shape names (str) and values are sets of block IDs (int) belonging to that shape.

low_brightness_min (int): Minimum grayscale value (0-255) for low-brightness blocks. Default: 0.

low_brightness_max (int): Maximum grayscale value (0-255) for low-brightness blocks. Default: 100.

high_brightness_min (int): Minimum grayscale value (0-255) for high-brightness blocks. Default: 155.

high_brightness_max (int): Maximum grayscale value (0-255) for high-brightness blocks. Default: 255.

show_ids (bool): Set to True to display block ID numbers, False to hide. Default: False.

id_color (str): Color string for the block ID text. Default: 'lime'.

id_font_size (int): Font size for the block ID text. Default: 10.

5. Available Shape Names

The following shape names are defined by default in config["shapes"] and can be used with set_target_shape() or passed to run_continuous():

"circle"

"filled_square"

"hollow_square"

"cross"

"x_shape"

"h_shape"

"arrow_up"

"arrow_down"

"horizontal_line"

"vertical_line"

"hollow_square_left"

"hollow_square_right"

"double_hollow_square"

"none" (Turns off highlighting)

You can add your own shapes by defining new key-value pairs in the shapes dictionary within your custom configuration. The value should be a set of integer block IDs.
