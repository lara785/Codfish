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
    # Add the new sound level
