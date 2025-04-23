UniHiker Dot Matrix Display Library
 A Python library for creating an animated dot matrix effect on a UniHiker screen. Display predefined shapes using blocks of flickering dots, with different brightness levels for highlighted and background blocks.

Features
Displays shapes using a grid of blocks.

Animates dots within blocks with random brightness flickering.

Supports different brightness ranges for highlighted (shape) and background blocks.

Configurable dot size, spacing, animation speed, and update rates.

Object-oriented structure.

Includes predefined shapes (circle, squares, arrows, lines, etc.).

Allows adding custom shapes.

Requirements
UniHiker board

UniHiker Python library (pinpong.extension.unihiker) installed and working.

Installation / Setup
Save the Library: Download or copy the library code (containing the DotMatrixDisplay, _Dot, and _Block classes) and save it as dot_matrix_lib.py on your UniHiker device. Place it in the same directory as the script where you intend to use it, or in a location included in your Python path.

Basic Usage
Here's a simple example demonstrating how to import and run the display with default settings:

# main_program.py
import time
from dot_matrix_lib import DotMatrixDisplay # Assuming library is saved as dot_matrix_lib.py

# 1. Create an instance of the display
#    Uses default configuration unless a custom 'config' dict is passed
display = DotMatrixDisplay()

# 2. Run the continuous animation loop
#    This blocks until Ctrl+C is pressed.
#    Specify the initial shape to show.
try:
    display.run_continuous(initial_shape="circle")
except KeyboardInterrupt:
    print("Program interrupted by user.")
# Cleanup (clearing the screen) is handled automatically by run_continuous

print("Main program finished.")

API Reference (DotMatrixDisplay Class)
__init__(self, config=None)

Initializes the display controller.

Calculates layout, creates internal block/dot representations, and performs initial screen clear.

config (dict, optional): A dictionary to override default configuration values (see Configuration section below).

set_target_shape(self, shape_name)

Sets the currently active shape to be highlighted. Blocks belonging to this shape will use the "high" brightness settings.

shape_name (str): The name of the shape (must be a key in config["shapes"]). Use "none" for no highlighting.

Note: Automatically redraws blocks that transition from high to low brightness for a cleaner visual change.

update_frame(self)

Updates a single frame of the animation.

Selects a random percentage of dots (based on update_percentage_high and update_percentage_low) and redraws them with appropriate random brightness.

Call this repeatedly in your own custom loop if not using run_continuous().

run_continuous(self, initial_shape="circle")

Starts and manages the main animation loop using a non-blocking delay.

Continuously calls update_frame() based on config["animation_interval"].

Prints status (frame count, time, current shape) to the console.

Runs until interrupted by Ctrl+C.

initial_shape (str, optional): The name of the shape to display initially (defaults to "circle").

Calls cleanup() automatically upon exit.

cleanup(self)

Attempts to clear the UniHiker screen by drawing a black rectangle.

Called automatically by run_continuous() but can be called manually if needed.

Configuration
Customize the display by passing a config dictionary when creating the DotMatrixDisplay instance.

my_config = {
    "dot_size": 10,
    "animation_interval": 0.05,
    # ... other overrides
}
display = DotMatrixDisplay(config=my_config)

Available Options (with defaults):

dot_size (int): Pixel size (width/height) of each dot. Default: 12.

dot_spacing (int): Base spacing used for layout calculations. Default: 6.

bg_color (str): Background color (e.g., 'black', '#000000'). Default: 'black'.

block_size (int): Conceptual grid size for layout. Default: 6.

block_gap_dots (int): Gap between blocks in layout units. Default: 2.

super_dot_offset (int): Pixel offset from block center for the 4 dots. Default: 8.

animation_interval (float): Target time (seconds) between frame updates. Default: 0.02.

update_percentage_high (float): Fraction (0.0-1.0) of high-brightness dots updated per frame. Default: 0.25.

update_percentage_low (float): Fraction (0.0-1.0) of low-brightness dots updated per frame. Default: 0.05.

shapes (dict): Dictionary mapping shape names (str) to sets of block IDs (int). See below.

low_brightness_min / low_brightness_max (int): Grayscale range (0-255) for background blocks. Defaults: 0 / 100.

high_brightness_min / high_brightness_max (int): Grayscale range (0-255) for highlighted blocks. Defaults: 155 / 255.

show_ids (bool): Display block ID numbers? Default: False.

id_color (str): Color for block IDs. Default: 'lime'.

id_font_size (int): Font size for block IDs. Default: 10.

Available Shapes
The following shape names are predefined in the default configuration:

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

"none" (No highlighted blocks)

Adding Custom Shapes
Define your own shapes by adding entries to the shapes dictionary in your custom configuration:

my_shapes = {
    # Keep existing shapes if needed by copying from DEFAULT_CONFIG["shapes"]
    **DEFAULT_CONFIG["shapes"], # Optional: include defaults
    # Add your custom shape
    "my_smiley": {6, 8, 16, 18, 27}, # Example block IDs for a smiley
}

my_config = {
    "shapes": my_shapes
}

display = DotMatrixDisplay(config=my_config)
display.run_continuous(initial_shape="my_smiley")

(Remember to determine the correct block IDs based on the 5x7 grid layout shown in the library's code comments or by enabling show_ids temporarily.)

Example: Cycling Shapes
See the example script main_cycle_program.py (provided previously) for how to manually control the animation loop and cycle through different shapes using display.set_target_shape() and display.update_frame().
