import board
import analogio
from adafruit_matrixportal.matrix import Matrix
import time
import socket
import wifi
import socketpool

# Initialize microphone input (replace with correct analog pin)
mic = analogio.AnalogIn(board.A0)  # Assuming A0 is the analog input pin

# Initialize the LED matrix for 128x64
matrix = Matrix(width=128, height=64)
display = matrix.display

# Wi-Fi credentials
SSID = 'your_wifi_ssid'
PASSWORD = 'your_wifi_password'

# UDP settings
UDP_IP = "0.0.0.0"  # Listen on all available IPs
UDP_PORT = 4210  # Arbitrary port for UDP communication
TRIGGER_MESSAGE = "show_evil"

# Parameters for smoothing
SAMPLES = 10  # Number of samples to average
sound_history = [0] * 128  # Initialize a buffer to store sound values for the waveform

# Clap detection settings
CLAP_THRESHOLD = 30000  # Set this to a value that corresponds to a loud clap
CLAP_TIMEOUT = 0.5  # Time window in seconds for consecutive claps
CLAP_COUNT_REQUIRED = 3  # Number of claps needed

# Variables to track claps
last_clap_time = 0
clap_count = 0

# Time-based display settings
last_display_time = time.monotonic()  # Track the last time names were displayed
DISPLAY_INTERVAL = 3600  # 1 hour in seconds

# List of names to display
names = ["Ema Pinheiro", "Diana Faria", "Laura Costa", "Tiago Salgado", "Dinis Costa", "Sleep Deprived Loon"]

# Function to connect to Wi-Fi
def connect_wifi():
    wifi.radio.connect(SSID, PASSWORD)
    print("Connected to Wi-Fi")

# Function to get smoothed sound level
def get_smoothed_sound_level():
    # Perform a simple moving average over SAMPLES readings to smooth the sound level
    total = 0
    for _ in range(SAMPLES):
        total += mic.value  # Read from the microphone
        time.sleep(0.01)  # Small delay between samples
    # Scale the averaged value to fit the display height (0 to 64)
    return int((total / SAMPLES) / 65535 * 64)

# Function to update the waveform
def update_waveform(new_level):
    # Shift the previous data in the history buffer to the left
    for i in range(127):
        sound_history[i] = sound_history[i + 1]
    # Add the new sound level to the end of the buffer
    sound_history[127] = new_level

# Birthday cake graphic (simple pixel art)
def draw_birthday_cake():
    display.fill(0)  # Clear the display
    # Example cake drawing
    for x in range(40, 90):
        display.pixel(x, 50, (255, 165, 0))  # Orange for base
    for x in range(50, 80):
        display.pixel(x, 45, (255, 0, 0))    # Red for middle
    for x in range(60, 70):
        display.pixel(x, 40, (255, 255, 0))  # Yellow for top
    # Draw candles
    display.pixel(62, 38, (255, 255, 255))  # White for candle 1
    display.pixel(68, 38, (255, 255, 255))  # White for candle 2
    display.show()

# Function to display names on the matrix
def display_names():
    display.fill(0)  # Clear the display
    y_pos = 10  # Starting Y position for text
    for name in names:
        display.text(name, 10, y_pos, (255, 255, 255))  # White text
        y_pos += 10  # Move down for each name
    display.show()
    time.sleep(5)  # Display for 5 seconds
    display.fill(0)  # Clear display after showing names
    display.show()

# Function to show the evil character on the matrix
def display_evil_character():
    display.fill(0)  # Clear the display
    # Define an evil character in pixel art (this is just a simple example)
    for x in range(40, 90):
        display.pixel(x, 50, (255, 0, 0))  # Red for evil character's body
    for x in range(50, 80):
        display.pixel(x, 45, (255, 0, 0))  # Red for evil character's middle
    for x in range(60, 70):
        display.pixel(x, 40, (255, 0, 0))  # Red for evil character's head
    # Add eyes
    display.pixel(55, 43, (255, 255, 255))  # Left eye
    display.pixel(65, 43, (255, 255, 255))  # Right eye
    display.show()

# Function to listen for special UDP packets
def listen_for_udp():
    pool = socketpool.SocketPool(wifi.radio)
    udp_socket = pool.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP, UDP_PORT))
    
    print(f"Listening for UDP packets on port {UDP_PORT}...")

    while True:
        # Wait for UDP packets
        data, addr = udp_socket.recvfrom(1024)  # Buffer size 1024 bytes
        message = data.decode("utf-8").strip()

        # Check if the received message is the special trigger message
        if TRIGGER_MESSAGE in message:
            print(f"Received trigger from {addr}: {message}")
            display_evil_character()  # Display the evil character when the special packet is received
            time.sleep(5)  # Display the evil character for 5 seconds
            display.fill(0)  # Clear the screen after the character is displayed
            display.show()

# Main loop
connect_wifi()  # Connect to Wi-Fi
listen_for_udp()  # Start listening for UDP packets

while True:
    # Get the current sound level
    sound_level = get_smoothed_sound_level()

    # Detect a clap based on threshold
    if sound_level > CLAP_THRESHOLD:
        current_time = time.monotonic()

        # Check if this is within the clap timeout window
        if current_time - last_clap_time < CLAP_TIMEOUT:
            clap_count += 1
        else:
            # Reset the clap count if it's outside the timeout window
            clap_count = 1

        last_clap_time = current_time

    # If three claps are detected, show the birthday cake
    if clap_count >= CLAP_COUNT_REQUIRED:
        draw_birthday_cake()
        time.sleep(5)  # Show cake for 5 seconds
        clap_count = 0  # Reset clap count after showing cake

    # Update waveform with new sound level
    update_waveform(sound_level)

    # Clear the display
    display.fill(0)

    # Draw the waveform as a line across the matrix
    for x in range(128):
        # Plot the sound history as vertical positions
        y = 63 - sound_history[x]  # Invert to match display coordinates
        display.pixel(x, y, (0, 255, 255))  # Cyan color for the waveform

    # Show the updated display
    display.show()

    # Check if it's time to display names (every 1 hour)
    current_time = time.monotonic()
    if current_time - last_display_time >= DISPLAY_INTERVAL:
        display_names()  # Display the names
        last_display_time = current_time  # Update last display time
