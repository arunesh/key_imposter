import pyaudio
import wave
import os
import time
import random
import threading
from pynput.keyboard import Controller

# --- Configuration ---
SOUNDS_DIR = "keystroke_sounds" # Must match the output dir from the recorder

# Create a keyboard controller instance
keyboard = Controller()

def play_wav_task(filepath):
    """
    Plays a WAV file. This function is designed to be run in a separate thread
    to avoid blocking the main typing simulation.
    """
    try:
        with wave.open(filepath, 'rb') as wf:
            # Each thread needs its own PyAudio instance
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
                
            stream.stop_stream()
            stream.close()
            p.terminate()
    except FileNotFoundError:
        # It's okay if some sounds are missing, we just won't play them.
        pass
    except Exception as e:
        print(f"\n[Error playing sound {filepath}: {e}]")


def simulate_typing(text):
    """
    Simulates typing by playing keystroke sounds and injecting characters
    into the active window.
    """
    print(f"--- Simulating Typing ---")
    print("Click on the window where you want the text to be typed.")
    for i in range(5, 0, -1):
        print(f"Starting in {i}...", end='\r', flush=True)
        time.sleep(1)
    
    print("Starting simulation...      ") # Extra spaces to clear line

    for char in text:
        # --- 1. Play Sound (in background) ---
        # We find the sound for the lowercase version of the key.
        char_lower = char.lower()
        if 'a' <= char_lower <= 'z':
            sound_file = os.path.join(SOUNDS_DIR, f"{char_lower}.wav")
            # Start the sound playback in a non-blocking background thread
            sound_thread = threading.Thread(target=play_wav_task, args=(sound_file,), daemon=True)
            sound_thread.start()

        # --- 2. Inject Keystroke ---
        # The controller handles uppercase, punctuation, etc., automatically.
        keyboard.type(char)

        # --- 3. Pause Realistically ---
        # Add a human-like, slightly random delay between keystrokes.
        if char == ' ':
            # Longer pause for spacebar
            delay = random.uniform(0.12, 0.25)
        else:
            # Shorter pause for regular keys
            delay = random.uniform(0.04, 0.15)
        
        time.sleep(delay)

if __name__ == "__main__":
    # Check if the sounds directory exists
    if not os.path.exists(SOUNDS_DIR) or not os.listdir(SOUNDS_DIR):
        print(f"Error: The '{SOUNDS_DIR}' directory is missing or empty.")
        print("Please run the 'record_keys.py' script first to generate the sounds.")
    else:
        sentence_to_type = "Hello world! This is a real typing simulation on macOS. Hope this works."
        try:
            simulate_typing(sentence_to_type)
            print("\nSimulation complete.")
        except Exception as e:
            print(f"\nAn error occurred. Did you grant Accessibility permissions? Error: {e}")
