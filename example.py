# main_thread_program.py
import time
import sys
import threading # Import the threading module
from unihikerDotMatrix.unihikerDotMatrix import DotMatrixDisplay # Import the library class

# --- Configuration for this example ---
# (Keep shape definitions accessible if needed, but they are primarily used by the library)
# SHAPE_CYCLE = [...] # No longer needed for cycling

# --- Optional: Define custom configuration for the display ---
my_config = {
    "dot_size": 10,
    "animation_interval": 0.02, # Target delay between frame updates in the thread
    "update_percentage_high": 0.3,
    "update_percentage_low": 0.1,
    "show_ids": False
}

# --- Global flag to signal the animation thread to stop ---
stop_animation_flag = threading.Event()

# --- Animation Thread Function ---
def animation_worker(display_instance):
    """
    This function runs in a separate thread and continuously updates the display.
    """
    print("[Animation Thread] Started.")
    last_update_time = time.monotonic()
    frame_counter = 0 # Local frame counter for the thread if needed

    while not stop_animation_flag.is_set():
        current_monotonic_time = time.monotonic()

        # --- Frame Update Logic (Non-Blocking) ---
        if current_monotonic_time - last_update_time >= display_instance.config["animation_interval"]:
            display_instance.update_frame() # Update one frame
            frame_counter += 1
            last_update_time = current_monotonic_time # Reset the update timer
        # ---

        # --- Small sleep to yield CPU ---
        # Prevents the thread from consuming 100% CPU if interval is very small
        # or update_frame is very fast.
        time.sleep(0.001)

    print("[Animation Thread] Stopped.")


# --- Main Program ---
if __name__ == "__main__":
    print("Initializing Dot Matrix Display...")
    # Create an instance of the display, potentially with custom config
    display = DotMatrixDisplay(config=my_config)

    # Check if GUI initialized successfully
    if not display.gui:
        print("Exiting program due to GUI initialization failure.", file=sys.stderr)
        sys.exit(1)

    # Set an initial shape
    initial_shape = "circle"
    display.set_target_shape(initial_shape)
    print(f"Initial shape set to: {initial_shape}")

    # Create and start the animation thread
    animation_thread = threading.Thread(target=animation_worker, args=(display,), daemon=True)
    # Setting daemon=True means the thread will exit automatically if the main program exits
    # However, we'll use the Event for cleaner shutdown.
    animation_thread.start()

    print("\nAnimation running in background.")
    print("Enter a shape name to change the display, or 'quit' to exit.")

    try:
        while True: # Loop to get user input
            # --- Prompt for shape ---
            available_shapes = list(display.config['shapes'].keys())
            print("\nAvailable shapes:")
            for shape in available_shapes:
                print(f"- {shape}")
            print("- quit (to exit)")
            sys.stdout.flush()

            try:
                user_input = input("Enter shape name or 'quit': ").strip().lower()
            except EOFError:
                print("\nInput stream closed. Exiting.")
                user_input = "quit" # Treat EOF as quit
            except KeyboardInterrupt:
                 print("\nCtrl+C detected during input. Exiting.")
                 user_input = "quit" # Treat Ctrl+C as quit

            if user_input == "quit":
                break # Exit the input loop

            # Validate input and set shape in the display object
            # The animation thread will pick up the change on its next update checks
            if user_input in display.config['shapes']:
                display.set_target_shape(user_input)
            else:
                print(f"Invalid shape '{user_input}'. Shape not changed.")
            # ---

    except KeyboardInterrupt:
        print("\nCtrl+C detected in main loop. Exiting.")
    finally:
        # --- Signal the animation thread to stop ---
        print("Stopping animation thread...")
        stop_animation_flag.set()

        # --- Wait for the animation thread to finish ---
        animation_thread.join(timeout=1.0) # Wait max 1 second
        if animation_thread.is_alive():
            print("Warning: Animation thread did not stop cleanly.", file=sys.stderr)

        # --- Cleanup the display ---
        display.cleanup()

    print("Main program finished.")

