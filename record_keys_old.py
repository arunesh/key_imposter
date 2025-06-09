import os
import threading
import time
import wave
import pyaudio
from pynput import keyboard

# --- Configuration ---
OUTPUT_DIR = "my_keyboard_sounds"  # Directory to save the recordings
RECORD_SECONDS = 0.2  # Duration of each key press recording in seconds
IS_RECORDING = False  # Global flag to prevent overlapping recordings

# --- Audio Settings ---
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate
CHUNK = 1024  # Buffer size

# --- Key Press Management ---
# This set will keep track of keys that are currently held down
# to prevent continuous recording if a key is held.
pressed_keys = set()

# --- Special Key Mapping ---
# Maps pynput's special keys to the filenames we want.
# This ensures compatibility with the injector script's key_code_map.
SPECIAL_KEY_MAP = {
    keyboard.Key.space: ' ',
    keyboard.Key.enter: 'return',
    keyboard.Key.backspace: 'backspace',
    keyboard.Key.esc: 'escape',
    keyboard.Key.cmd: 'command',
    keyboard.Key.shift: 'shift',
    keyboard.Key.alt: 'option', # 'alt' is Option on Mac
    keyboard.Key.ctrl: 'control',
}

def record_audio(filename_base):
    """Records a short audio clip and saves it to a WAV file."""
    global IS_RECORDING
    if IS_RECORDING:
        return # Don't start a new recording if one is already in progress

    IS_RECORDING = True
    
    filepath = os.path.join(OUTPUT_DIR, f"{filename_base}.wav")
    
    # Skip if the file already exists
    if os.path.exists(filepath):
        print(f"Sound for '{filename_base}' already exists. Skipping.")
        IS_RECORDING = False
        return

    print(f"Recording sound for '{filename_base}'...")

    audio = pyaudio.PyAudio()
    
    # Start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []
    
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save the recording to a WAV file
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print(f" ✓ Saved {filepath}")
    
    # A small delay to ensure the microphone "settles" and avoids echo/feedback
    # if the user types extremely fast.
    time.sleep(0.1) 
    IS_RECORDING = False

def get_key_name(key):
    """Translates a pynput key object into a consistent string name."""
    if key in SPECIAL_KEY_MAP:
        return SPECIAL_KEY_MAP[key]
    try:
        # For regular alphanumeric keys
        return key.char
    except AttributeError:
        # For other special keys not in our map (e.g., F1, Home)
        return key.name

def on_press(key):
    """Callback function executed when a key is pressed."""
    key_name = get_key_name(key)
    
    if key_name is None:
        return
        
    # Stop the listener if Escape is pressed
    if key == keyboard.Key.esc:
        print("Escape pressed, stopping recorder...")
        return False # This stops the listener

    # If the key is already held down, do nothing.
    if key_name in pressed_keys:
        return

    # Add the key to the set of pressed keys and start recording in a new thread
    pressed_keys.add(key_name)
    
    # Use a thread to record audio so it doesn't block the main key listener
    thread = threading.Thread(target=record_audio, args=(key_name,))
    thread.start()

def on_release(key):
    """Callback function executed when a key is released."""
    key_name = get_key_name(key)
    if key_name in pressed_keys:
        pressed_keys.remove(key_name)

def main():
    """Main function to set up and run the recorder."""
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
        
    print("--- Keystroke Sound Recorder ---")
    print(f"Recording duration per key: {RECORD_SECONDS}s")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nPress any key to record its sound.")
    print("Recordings for existing keys will be skipped.")
    print("\n>>> PRESS 'Esc' KEY TO STOP THE RECORDER. <<<\n")

    # Set up and start the listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
        
    print("\nRecorder stopped. Your sounds are saved.")

if __name__ == "__main__":
    main()
