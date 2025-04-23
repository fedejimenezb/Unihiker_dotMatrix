# Import the necessary library components
from unihiker import GUI
import time
import random # Import the random module
import sys # Import sys for flushing output
import datetime # Import datetime for timestamp

# --- Default Configuration (can be overridden during instantiation) ---
DEFAULT_CONFIG = {
    "dot_size": 12,        # Size of the dots (consistent now)
    "dot_spacing": 6,      # Distance between the CENTERS of original dots (used for layout)
    "bg_color": 'black',   # Background color of the screen / darkest shade
    "block_size": 6,       # Original dots per side (used for layout calculation)
    "block_gap_dots": 2,   # Number of original dot positions to skip between blocks
    "super_dot_offset": 8, # Offset from block center for placing 2x2 super dots
    "animation_interval": 0.02, # Target interval (in seconds) between frame updates
    "update_percentage_high": 0.25, # Percentage of HIGH brightness dots to update each frame
    "update_percentage_low": 0.05,  # Percentage of LOW brightness dots to update each frame

    # Shape Definitions (Based on a 5x7 grid)
    #  0  1  2  3  4
    #  5  6  7  8  9
    # 10 11 12 13 14
    # 15 16 17 18 19
    # 20 21 22 23 24
    # 25 26 27 28 29
    # 30 31 32 33 34
    "shapes": {
        "circle": {7, 11, 12, 13, 16, 17, 18, 21, 22, 23, 27},
        "filled_square": {11, 12, 13, 16, 17, 18, 21, 22, 23},
        "hollow_square": {11, 12, 13, 16, 18, 21, 22, 23},
        "cross": {7, 12, 16, 17, 18, 22, 27},
        "x_shape": {7, 9, 11, 13, 17, 21, 23, 25, 27},
        "h_shape": {11, 13, 16, 17, 18, 21, 23},
        "arrow_up": {6, 7, 8, 12, 17, 22, 27},
        "arrow_down": {7, 12, 17, 22, 26, 27, 28},
        "horizontal_line": {15, 16, 17, 18, 19},
        "vertical_line": {2, 7, 12, 17, 22, 27, 32},
        "hollow_square_left": {21, 22, 23, 26, 28, 31, 32, 33}, # Center 27
        "hollow_square_right": {1, 2, 3, 6, 8, 11, 12, 13},    # Center 7
        "double_hollow_square": {1, 2, 3, 6, 8, 11, 12, 13, 21, 22, 23, 26, 28, 31, 32, 33},
        "none": set() # Option for no highlighted shape
    },

    # Brightness Configuration
    "low_brightness_min": 0,
    "low_brightness_max": 100,
    "high_brightness_min": 155,
    "high_brightness_max": 255,

    # ID Display Configuration
    "show_ids": False,
    "id_color": 'lime',
    "id_font_size": 10,
}

# --- Helper Classes (Internal) ---

class _Dot:
    """Represents a single dot (super dot) on the display."""
    def __init__(self, x, y, group_id):
        self.x = x # Top-left x coordinate
        self.y = y # Top-left y coordinate
        self.group_id = group_id

class _Block:
    """Represents a block (group) of dots."""
    def __init__(self, id, center_x, center_y):
        self.id = id
        self.center_x = center_x
        self.center_y = center_y
        self.dots = [] # List to hold _Dot objects belonging to this block
        self.is_high_brightness = False # Flag indicating if this block is part of the target shape

    def add_dot(self, dot_obj):
        """Adds a _Dot object to this block."""
        self.dots.append(dot_obj)

    def set_highlight(self, is_high):
        """Sets the highlight status for this block."""
        changed = self.is_high_brightness != is_high
        self.is_high_brightness = is_high
        return changed

    def get_random_brightness(self, config):
        """Returns a random brightness value based on highlight status."""
        if self.is_high_brightness:
            return random.randint(config["high_brightness_min"], config["high_brightness_max"])
        else:
            return random.randint(config["low_brightness_min"], config["low_brightness_max"])

    def draw_id(self, gui, config):
        """Draws the block's ID number on the screen."""
        if not config["show_ids"] or not gui:
            return
        try:
            gui.draw_text(
                x=self.center_x,
                y=self.center_y,
                text=str(self.id),
                font_size=config["id_font_size"],
                color=config["id_color"],
                origin='center'
            )
        except Exception as e:
            try:
                 font_size = config["id_font_size"]
                 offset_x = int(font_size * 0.3 * len(str(self.id)))
                 offset_y = int(font_size * 0.5)
                 gui.draw_text(
                    x=self.center_x - offset_x,
                    y=self.center_y - offset_y,
                    text=str(self.id),
                    font_size=font_size,
                    color=config["id_color"]
                )
            except Exception as e2:
                 print(f"Error drawing text ID {self.id} (fallback failed): {e2}", file=sys.stderr, flush=True)

    def redraw_dots(self, gui, config, force_brightness_range=None):
        """Redraws all dots in this block, optionally forcing a specific brightness range."""
        for dot in self.dots:
            if force_brightness_range is not None:
                 if force_brightness_range == 'low':
                     gray_level = random.randint(config["low_brightness_min"], config["low_brightness_max"])
                 elif force_brightness_range == 'high':
                      gray_level = random.randint(config["high_brightness_min"], config["high_brightness_max"])
                 else:
                     gray_level = force_brightness_range
            else:
                gray_level = self.get_random_brightness(config)

            hex_val = f'{gray_level:02x}'
            dot_color = f'#{hex_val}{hex_val}{hex_val}'
            try:
                gui.draw_rect(x=dot.x, y=dot.y, w=config['dot_size'], h=config['dot_size'],
                              fill=dot_color, outline=dot_color)
            except Exception as e:
                print(f"Error redrawing dot in block {self.id} at ({dot.x},{dot.y}): {e}", file=sys.stderr, flush=True)


# --- Main Library Class ---

class DotMatrixDisplay:
    """
    Manages a dot matrix display animation on the UniHiker screen.

    Allows setting predefined shapes to be displayed with higher brightness
    against a dimmer background, both animated with random flickering.
    """
    def __init__(self, config=None):
        """
        Initializes the DotMatrixDisplay.

        Args:
            config (dict, optional): A dictionary overriding default configuration values.
                                     Defaults to DEFAULT_CONFIG.
        """
        # Merge provided config with defaults
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

        try:
            self.gui = GUI()
        except Exception as e:
             print(f"Error initializing UniHiker GUI: {e}", file=sys.stderr, flush=True)
             print("Please ensure the UniHiker library is installed and configured correctly.", file=sys.stderr, flush=True)
             # Optionally, re-raise the exception or exit if GUI is critical
             # raise e
             self.gui = None # Set gui to None if initialization fails
             # Or exit: sys.exit(1)


        self.screen_width = 240 # Assuming fixed size for now
        self.screen_height = 320
        self.blocks = {} # Dictionary to store blocks by ID for easy lookup
        self.all_dots = [] # List of all _Dot objects (representing super dots)
        self.num_total_dots = 0
        self.selected_shape_name = "none" # Keep track of the current shape name

        self._calculate_layout_and_create_objects()
        self.initialize_display() # Perform initial clear and draw

    def _calculate_layout_and_create_objects(self):
        """Calculates grid layout and creates _Block and _Dot objects."""
        # --- Calculations for Centering (uses original block_size for layout) ---
        orig_dot_size = 4 # Need original size for accurate block dimension calc
        dot_spacing = self.config["dot_spacing"]
        block_size = self.config["block_size"] # Original 6x6 layout
        block_gap_dots = self.config["block_gap_dots"]
        super_dot_size = self.config["dot_size"] # The size for drawing
        super_dot_offset = self.config["super_dot_offset"]

        # Calculate the pixel dimension of the original 6x6 block area
        block_pixel_dimension = (block_size - 1) * dot_spacing + orig_dot_size
        gap_pixel_size = block_gap_dots * dot_spacing

        num_blocks_x = 0
        if block_pixel_dimension <= self.screen_width:
            current_width = block_pixel_dimension
            num_blocks_x = 1
            while current_width + gap_pixel_size + block_pixel_dimension <= self.screen_width:
                current_width += gap_pixel_size + block_pixel_dimension
                num_blocks_x += 1
        num_blocks_y = 0
        if block_pixel_dimension <= self.screen_height:
            current_height = block_pixel_dimension
            num_blocks_y = 1
            while current_height + gap_pixel_size + block_pixel_dimension <= self.screen_height:
                current_height += gap_pixel_size + block_pixel_dimension
                num_blocks_y += 1

        if num_blocks_x > 0: total_grid_width = (num_blocks_x * block_pixel_dimension) + max(0, (num_blocks_x - 1)) * gap_pixel_size
        else: total_grid_width = 0
        if num_blocks_y > 0: total_grid_height = (num_blocks_y * block_pixel_dimension) + max(0, (num_blocks_y - 1)) * gap_pixel_size
        else: total_grid_height = 0
        padding_x = (self.screen_width - total_grid_width) // 2
        padding_y = (self.screen_height - total_grid_height) // 2

        first_orig_dot_center_x = padding_x + orig_dot_size // 2
        first_orig_dot_center_y = padding_y + orig_dot_size // 2
        total_block_step = block_pixel_dimension + gap_pixel_size

        # --- Create Blocks and the 4 Super Dots per block ---
        self.blocks = {}
        self.all_dots = []
        group_id_counter = 0

        # print("Calculating dot positions and group info...") # Less verbose for library
        for block_idx_y in range(num_blocks_y):
            block_start_orig_dot_center_y = first_orig_dot_center_y + block_idx_y * total_block_step
            for block_idx_x in range(num_blocks_x):
                block_start_orig_dot_center_x = first_orig_dot_center_x + block_idx_x * total_block_step
                block_center_x = block_start_orig_dot_center_x + (block_pixel_dimension - orig_dot_size) / 2
                block_center_y = block_start_orig_dot_center_y + (block_pixel_dimension - orig_dot_size) / 2
                current_group_id = group_id_counter
                current_block = _Block(id=current_group_id, center_x=int(block_center_x), center_y=int(block_center_y))
                self.blocks[current_group_id] = current_block
                for j in range(2):
                    for i in range(2):
                        dot_center_x = block_center_x + (-super_dot_offset if i == 0 else super_dot_offset)
                        dot_center_y = block_center_y + (-super_dot_offset if j == 0 else super_dot_offset)
                        rect_x = int(dot_center_x - super_dot_size // 2)
                        rect_y = int(dot_center_y - super_dot_size // 2)
                        if rect_x >= 0 and rect_y >= 0 and rect_x + super_dot_size <= self.screen_width and rect_y + super_dot_size <= self.screen_height:
                             new_dot = _Dot(x=rect_x, y=rect_y, group_id=current_group_id)
                             current_block.add_dot(new_dot)
                             self.all_dots.append(new_dot)
                group_id_counter += 1

        self.num_total_dots = len(self.all_dots)
        # print(f"Calculated {self.num_total_dots} super dot positions across {len(self.blocks)} groups.")

    def initialize_display(self):
        """Clears the screen and draws initial background dots."""
        if not self.gui: return # Don't draw if GUI failed
        # print(f"Clearing screen with {self.config['bg_color']}...")
        self.gui.draw_rect(x=0, y=0, w=self.screen_width, h=self.screen_height,
                           outline=self.config['bg_color'], fill=self.config['bg_color'])
        # print("Drawing initial background dots...")
        for dot in self.all_dots:
             self.gui.draw_rect(x=dot.x, y=dot.y, w=self.config['dot_size'], h=self.config['dot_size'],
                                fill=self.config['bg_color'], outline=self.config['bg_color'])
        self.draw_ids()

    def set_target_shape(self, shape_name):
        """
        Sets the active shape to be highlighted.

        Args:
            shape_name (str): The name of the shape (key in config['shapes']).
                              Use "none" to turn off highlighting.
        """
        if not self.gui: return # Don't operate if GUI failed
        self.selected_shape_name = shape_name
        # print(f"Setting target shape to: {shape_name}") # Less verbose for library
        target_group_ids = self.config["shapes"].get(shape_name, set())
        if not target_group_ids and shape_name != "none":
            print(f"Warning: Shape '{shape_name}' not found. Using 'none'.", file=sys.stderr, flush=True)
            target_group_ids = self.config["shapes"]["none"]

        for block_id, block in self.blocks.items():
            is_target_high = block_id in target_group_ids
            status_changed = block.set_highlight(is_target_high)
            if status_changed and not block.is_high_brightness:
                 block.redraw_dots(self.gui, self.config, force_brightness_range='low')

    def draw_ids(self):
        """Draws all group IDs if enabled in config."""
        if not self.config["show_ids"] or not self.gui:
            return
        for block in self.blocks.values():
            block.draw_id(self.gui, self.config)

    def update_frame(self):
        """
        Updates one frame of the animation.

        This should be called repeatedly in the main loop of the controlling program.
        """
        if self.num_total_dots == 0 or not self.gui:
            return

        high_brightness_dots = [dot for dot in self.all_dots if self.blocks[dot.group_id].is_high_brightness]
        low_brightness_dots = [dot for dot in self.all_dots if not self.blocks[dot.group_id].is_high_brightness]

        if high_brightness_dots:
            num_to_update_high = max(1, int(len(high_brightness_dots) * self.config["update_percentage_high"]))
            dots_to_update = random.sample(high_brightness_dots, min(num_to_update_high, len(high_brightness_dots)))
            for dot in dots_to_update:
                parent_block = self.blocks[dot.group_id]
                gray_level = parent_block.get_random_brightness(self.config)
                hex_val = f'{gray_level:02x}'
                dot_color = f'#{hex_val}{hex_val}{hex_val}'
                try:
                    self.gui.draw_rect(x=dot.x, y=dot.y, w=self.config['dot_size'], h=self.config['dot_size'],
                                      fill=dot_color, outline=dot_color)
                except Exception as e:
                    print(f"Error updating high rect at ({dot.x},{dot.y}): {e}", file=sys.stderr, flush=True)

        if low_brightness_dots:
            num_to_update_low = max(1, int(len(low_brightness_dots) * self.config["update_percentage_low"]))
            if num_to_update_low == 0 and self.config["update_percentage_low"] > 0: num_to_update_low = 1
            dots_to_update = random.sample(low_brightness_dots, min(num_to_update_low, len(low_brightness_dots)))
            for dot in dots_to_update:
                parent_block = self.blocks[dot.group_id]
                gray_level = parent_block.get_random_brightness(self.config)
                hex_val = f'{gray_level:02x}'
                dot_color = f'#{hex_val}{hex_val}{hex_val}'
                try:
                    self.gui.draw_rect(x=dot.x, y=dot.y, w=self.config['dot_size'], h=self.config['dot_size'],
                                      fill=dot_color, outline=dot_color)
                except Exception as e:
                    print(f"Error updating low rect at ({dot.x},{dot.y}): {e}", file=sys.stderr, flush=True)

        self.draw_ids()

    def run_continuous(self, initial_shape="circle"):
        """
        Runs the main animation loop continuously using a non-blocking delay.

        Args:
            initial_shape (str, optional): The name of the shape to display initially.
                                           Defaults to "circle".
        """
        if not self.gui:
             print("Cannot run: GUI not initialized.", file=sys.stderr, flush=True)
             return

        self.set_target_shape(initial_shape) # Set the initial shape

        print("Starting continuous animation... Press Ctrl+C to stop.")

        frame_counter = 0
        last_print_time = time.time()
        last_update_time = time.monotonic()

        try:
            while True:
                current_monotonic_time = time.monotonic()
                current_wall_time = time.time()

                if current_monotonic_time - last_update_time >= self.config["animation_interval"]:
                    self.update_frame()
                    frame_counter += 1
                    last_update_time = current_monotonic_time

                if current_wall_time - last_print_time >= 1.0:
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"\rFrame: {frame_counter} | Time: {timestamp} | Shape: {self.selected_shape_name}", end="", flush=True)
                    last_print_time = current_wall_time

                time.sleep(0.001)

        except KeyboardInterrupt:
            print("\nExiting animation loop (Ctrl+C detected).")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clears the screen on exit."""
        print("Cleaning up...")
        if self.gui:
             try:
                 self.gui.draw_rect(x=0, y=0, w=self.screen_width, h=self.screen_height, outline='black', fill='black')
                 print("Screen cleared.")
             except Exception as e:
                 print(f"Error clearing screen during cleanup: {e}", file=sys.stderr, flush=True)
        print("Exited.")

# --- Example Usage (if run directly) ---
# This block is now intended only for testing the library itself.
# To use the library, import DotMatrixDisplay and instantiate it in another script.
if __name__ == "__main__":
    print("Running DotMatrixDisplay library example...")

    # Example: Override default config
    custom_config = {
        "show_ids": False,
        "animation_interval": 0.03
    }

    # Create an instance of the display
    # display = DotMatrixDisplay() # Use defaults
    display = DotMatrixDisplay(config=custom_config) # Use custom config

    # You can change the shape before running or during execution if you modify the run loop
    # display.set_target_shape("cross")

    # Run the continuous animation
    display.run_continuous(initial_shape="double_hollow_square")

