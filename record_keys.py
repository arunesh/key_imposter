import pyaudio
import wave
import os
import time
import sys

# These modules are for controlling the terminal to get single-character input
# They are standard on macOS and Linux, so no extra installation is needed.
import tty
import termios

# --- Audio Configuration ---
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1              # Mono
RATE = 44100              # 44.1kHz sampling rate
CHUNK = 1024              # Samples per buffer
RECORD_SECONDS = 0.4      # Duration of recording after key press
OUTPUT_DIR = "keystroke_sounds" # Directory to save the recordings

# --- Keys to Record ---
KEYS_TO_RECORD = "abcdefghijklmnopqrstuvwxyz"

def get_single_char():
    """
    Gets a single character from standard input without waiting for Enter.
    This is the key function that solves the input buffering problem.
    """
    # Get the file descriptor for the terminal
    fd = sys.stdin.fileno()
    # Save the original terminal settings
    old_settings = termios.tcgetattr(fd)
    try:
        # Put the terminal into raw mode. This makes it read key by key.
        tty.setraw(sys.stdin.fileno())
        # Read a single character
        ch = sys.stdin.read(1)
    finally:
        # ALWAYS restore the original terminal settings.
        # If you don't, your terminal will be messed up after the script exits.
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def record_audio_chunk(p, stream, seconds):
    """Records a short audio chunk from the stream."""
    frames = []
    num_chunks = int(RATE / CHUNK * seconds)
    # Give a tiny moment for the key sound to start before recording
    time.sleep(0.05) 
    for _ in range(num_chunks):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    return b''.join(frames)

def save_wave_file(filepath, frames, p):
    """Saves the recorded frames to a WAV file."""
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(frames)

def main():
    """
    Main function to orchestrate the recording of each keystroke.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    p = pyaudio.PyAudio()

    # Open a persistent audio stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("--- Keystroke Sound Recorder ---")
    print("This script will record the sound of each letter key you press.")
    print("For each letter, press the key firmly when prompted.")
    print("Ensure you are in a quiet environment for the best results.\n")
    print("Press Ctrl+C at any time to quit.")
    time.sleep(2)

    try:
        for char_to_record in KEYS_TO_RECORD:
            # Using flush=True ensures the prompt appears immediately
            print(f"[*] Please press the '{char_to_record.upper()}' key now...", end="", flush=True)
            
            # Wait for the correct key to be pressed
            while True:
                pressed_key = get_single_char()
                
                # Check for Ctrl+C to exit gracefully
                if ord(pressed_key) == 3: 
                    raise KeyboardInterrupt

                if pressed_key == char_to_record:
                    # Move to the next line after successful key press
                    print(f"  OK! Recording...")
                    break
                else:
                    # Optional: give feedback for wrong key press
                    # '\r' moves the cursor to the beginning of the line to overwrite it
                    print(f"\r[!] Wrong key. Please press '{char_to_record.upper()}'.", end="", flush=True)

            # The correct key was pressed, now record the audio
            frames = record_audio_chunk(p, stream, RECORD_SECONDS)
            
            # Save the recorded audio
            filename = f"{char_to_record}.wav"
            filepath = os.path.join(OUTPUT_DIR, filename)
            save_wave_file(filepath, frames, p)
            print(f"  -> Saved sound to {filepath}\n")
            
            # A small delay to prepare for the next key
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nRecording interrupted by user. Exiting.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("--- Cleaning up and closing audio stream. ---")
        # Cleanup
        if 'stream' in locals() and stream.is_active():
            stream.stop_stream()
            stream.close()
        if 'p' in locals():
            p.terminate()


if __name__ == "__main__":
    main()
