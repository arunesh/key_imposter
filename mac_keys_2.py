import time
import os
import pygame
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    kCGHIDEventTap,
    kCGEventKeyDown,
    kCGEventKeyUp,
    CGEventSourceCreate,
    kCGEventSourceStateHIDSystemState,
    CGEventSetFlags,
    kCGEventFlagMaskShift,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskAlternate
)

# --- Sound Configuration ---
SOUND_DIR = "keyboard_sounds"
try:
    # Initialize the pygame mixer
    pygame.mixer.init()
    # Load sounds into a dictionary for fast access
    SOUNDS = {
        'default': pygame.mixer.Sound(os.path.join(SOUND_DIR, "key_press.wav")),
        'space': pygame.mixer.Sound(os.path.join(SOUND_DIR, "space_press.wav")),
        'enter': pygame.mixer.Sound(os.path.join(SOUND_DIR, "enter_press.wav")),
        'backspace': pygame.mixer.Sound(os.path.join(SOUND_DIR, "backspace_press.wav")),
    }
    print("Keyboard sounds loaded successfully.")
except (pygame.error, FileNotFoundError) as e:
    print(f"Warning: Could not load sounds. Running in silent mode. Error: {e}")
    SOUNDS = None


# --- Key Code Mapping (Extended) ---
key_code_map = {
    'a': 0x00, 's': 0x01, 'd': 0x02, 'f': 0x03, 'h': 0x04,
    'g': 0x05, 'z': 0x06, 'x': 0x07, 'c': 0x08, 'v': 0x09,
    'b': 0x0B, 'q': 0x0C, 'w': 0x0D, 'e': 0x0E, 'r': 0x0F,
    'y': 0x10, 't': 0x11, 'o': 0x1F, 'u': 0x20, 'i': 0x22,
    'p': 0x23, 'l': 0x25, 'j': 0x26, 'k': 0x28, 'n': 0x2D,
    'm': 0x2E,
    ' ': 0x31,
    'return': 0x24,
    'backspace': 0x33,
    'escape': 0x35,
    'command': 0x37,
    'shift': 0x38,
    'option': 0x3A,
    'control': 0x3B,
}

def press_key_with_sound(key_name, flags=0):
    """
    Simulates a single key press and release, with accompanying sound.
    `key_name` should be a string from the key_code_map.
    """
    key_code = key_code_map.get(key_name)
    if key_code is None:
        print(f"Warning: Key '{key_name}' not found in key_code_map, skipping.")
        return

    # --- Play Sound ---
    if SOUNDS:
        # Determine which sound to play
        if key_name == ' ':
            sound_to_play = SOUNDS.get('space')
        elif key_name == 'return':
            sound_to_play = SOUNDS.get('enter')
        elif key_name == 'backspace':
            sound_to_play = SOUNDS.get('backspace')
        else:
            sound_to_play = SOUNDS.get('default')

        # Play the sound if it was found
        if sound_to_play:
            # .play() is non-blocking, perfect for our use case
            sound_to_play.play()

    # --- Post Keystroke Event ---
    source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
    keyDown = CGEventCreateKeyboardEvent(source, key_code, True)
    keyUp = CGEventCreateKeyboardEvent(source, key_code, False)

    if flags:
        CGEventSetFlags(keyDown, flags)
        CGEventSetFlags(keyUp, 0) # Release modifiers on key up

    CGEventPost(kCGHIDEventTap, keyDown)
    time.sleep(0.01) # A small delay can help the target app process the event
    CGEventPost(kCGHIDEventTap, keyUp)
    time.sleep(0.05) # Delay after key press for realism


def type_string(text):
    """
    Types a string character by character with sound.
    Handles uppercase letters by simulating a Shift press.
    """
    for char in text:
        key_name = char.lower()
        flags = 0

        if 'a' <= char <= 'z':
            press_key_with_sound(key_name)
        elif 'A' <= char <= 'Z':
            # For uppercase, press Shift + key
            press_key_with_sound(key_name, flags=kCGEventFlagMaskShift)
        elif char == ' ':
            press_key_with_sound(' ')
        else:
            print(f"Warning: Character '{char}' cannot be typed directly, skipping.")


def press_hotkey(key_name, *modifiers):
    """
    Simulates a hotkey press, e.g., Command-V, with sound.
    `modifiers` should be constants like kCGEventFlagMaskCommand.
    """
    # Combine all modifier flags
    combined_flags = 0
    for mod in modifiers:
        combined_flags |= mod

    # Pass the key name and flags to the main function
    press_key_with_sound(key_name, flags=combined_flags)


if __name__ == "__main__":
    # --- Example Usage ---
    print("Starting keystroke injection with sound in 5 seconds...")
    print("Quickly switch to a text editor or any input field.")
    time.sleep(5)

    # Example 1: Type a string with custom sounds
    print("Typing 'Hello World'...")
    type_string("Hello World")
    press_key_with_sound('return')
    press_key_with_sound('return')
    
    # Example 2: Demonstrate backspace sound
    type_string("oops")
    time.sleep(0.5)
    print("Correcting a typo...")
    press_key_with_sound('backspace')
    press_key_with_sound('backspace')
    press_key_with_sound('backspace')
    press_key_with_sound('backspace')

    # Example 3: Simulate hotkeys
    print("Simulating Command-A (Select All)...")
    type_string("Select this text")
    time.sleep(1)
    press_hotkey('a', kCGEventFlagMaskCommand)
    time.sleep(1)

    print("\nDone.")
