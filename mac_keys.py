import time
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
    kCGEventFlagMaskAlternate # Option key
)

# --- Key Code Mapping ---
# The API needs virtual key codes, not characters.
# This is a partial map. For a full list, see the link in the explanation below.
key_code_map = {
    'a': 0x00, 's': 0x01, 'd': 0x02, 'f': 0x03, 'h': 0x04,
    'g': 0x05, 'z': 0x06, 'x': 0x07, 'c': 0x08, 'v': 0x09,
    'b': 0x0B, 'q': 0x0C, 'w': 0x0D, 'e': 0x0E, 'r': 0x0F,
    'y': 0x10, 't': 0x11, 'o': 0x1F, 'u': 0x20, 'i': 0x22,
    'p': 0x23, 'l': 0x25, 'j': 0x26, 'k': 0x28, 'n': 0x2D,
    'm': 0x2E,
    ' ': 0x31, # Spacebar
    'return': 0x24,
    'escape': 0x35,
    'command': 0x37,
    'shift': 0x38,
    'option': 0x3A,
    'control': 0x3B,
}

def press_key(key_code, flags=0):
    """
    Simulates a single key press and release event.
    """
    # Create a system-wide event source
    source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

    # Create key down and key up events
    keyDown = CGEventCreateKeyboardEvent(source, key_code, True)
    keyUp = CGEventCreateKeyboardEvent(source, key_code, False)

    # Apply modifier flags if any
    if flags:
        CGEventSetFlags(keyDown, flags)
        # Note: Modifiers are typically released after the main key
        # For simplicity here, we release them with the key up event.
        # For complex combos, you might manage modifier up/down events separately.
        CGEventSetFlags(keyUp, 0) # Release modifiers on key up

    # Post the events to the system event stream
    CGEventPost(kCGHIDEventTap, keyDown)
    time.sleep(0.01) # Small delay between down and up
    CGEventPost(kCGHIDEventTap, keyUp)
    time.sleep(0.05) # Delay after key press

def type_string(text):
    """
    Types a string character by character.
    Handles uppercase letters by simulating a Shift press.
    """
    for char in text:
        if 'a' <= char <= 'z':
            press_key(key_code_map[char])
        elif 'A' <= char <= 'Z':
            # For uppercase, press Shift + key
            press_key(key_code_map[char.lower()], flags=kCGEventFlagMaskShift)
        elif char == ' ':
            press_key(key_code_map[' '])
        # Add more special character handling here if needed
        else:
            print(f"Warning: Character '{char}' not in key_code_map, skipping.")

def press_hotkey(key, *modifiers):
    """
    Simulates a hotkey press, e.g., Command-V
    `modifiers` should be constants like kCGEventFlagMaskCommand, etc.
    """
    source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
    key_code = key_code_map.get(key.lower())

    if key_code is None:
        print(f"Error: Key '{key}' not found in key_code_map.")
        return

    # Combine all modifier flags
    combined_flags = 0
    for mod in modifiers:
        combined_flags |= mod

    # Create and post the event
    keyDown = CGEventCreateKeyboardEvent(source, key_code, True)
    CGEventSetFlags(keyDown, combined_flags)
    CGEventPost(kCGHIDEventTap, keyDown)

    time.sleep(0.01)

    keyUp = CGEventCreateKeyboardEvent(source, key_code, False)
    # The keyUp event for the main key should not have modifier flags
    # In a real scenario, you'd release the modifier keys separately *after* this.
    # For a simple hotkey, this is often sufficient.
    CGEventPost(kCGHIDEventTap, keyUp)


if __name__ == "__main__":
    # --- Example Usage ---
    print("Starting keystroke injection in 5 seconds...")
    print("Quickly switch to a text editor or any input field.")
    time.sleep(5)

    # Example 1: Type a simple string
    print("Typing 'hello world'...")
    type_string("hello World")
    press_key(key_code_map['return'])

    # Example 2: Simulate a hotkey (Command-A to select all)
    print("Simulating Command-A (Select All)...")
    time.sleep(1)
    press_hotkey('a', kCGEventFlagMaskCommand)
    time.sleep(1)

    # Example 3: Simulate another hotkey (Command-C to copy)
    print("Simulating Command-C (Copy)...")
    press_hotkey('c', kCGEventFlagMaskCommand)
    time.sleep(1)
    
    # Example 4: Simulate paste (Command-V)
    print("Simulating Command-V (Paste)...")
    press_hotkey('v', kCGEventFlagMaskCommand)

    print("\nDone.")
