import board
import analogio
from adafruit_matrixportal.matrix import Matrix
import time
import random

# Initialize microphone input (replace with correct analog pin)
mic = analogio.AnalogIn(board.A0)  # Assuming A0 is the analog input pin

# Initialize the LED matrix for 128x64
matrix = Matrix(width=128, height=64)
display = matrix.display

# Clap detection settings
CLAP_THRESHOLD = 30000  # Set this to a value that corresponds to a loud clap
CLAP_TIMEOUT = 0.5  # Time window in seconds for consecutive claps

# Game settings
GRAVITY = 1
FLAP_STRENGTH = -8
PIPE_SPEED = 1
PIPE_GAP = 12  # Vertical gap size for pipes
BIRD_X = 20  # Bird's horizontal position (fixed)
PIPE_INTERVAL = 40  # Distance between pipes

# Game state variables
bird_y = 32  # Start the bird in the middle of the screen
bird_velocity = 0
pipes = []  # List of pipes (tuples of (x_position, gap_position))
score = 0
last_clap_time = 0

# Function to get smoothed sound level (for clap detection)
def get_smoothed_sound_level():
    # Perform a simple moving average to smooth the sound level
    total = 0
    for _ in range(10):
        total += mic.value  # Read from the microphone
        time.sleep(0.01)  # Small delay between samples
    return int(total / 10)

# Function to generate a new pipe
def generate_pipe():
    gap_y = random.randint(10, 64 - PIPE_GAP - 10)  # Random vertical gap position
    pipes.append([128, gap_y])  # New pipe starts off-screen

# Function to update the bird's position
def update_bird():
    global bird_y, bird_velocity

    # Apply gravity
    bird_velocity += GRAVITY
    bird_y += bird_velocity

    # Keep bird within bounds
    if bird_y < 0:
        bird_y = 0
        bird_velocity = 0
    elif bird_y > 63:
        bird_y = 63
        bird_velocity = 0

# Function to move the pipes and check for collisions
def update_pipes():
    global score

    for pipe in pipes:
        pipe[0] -= PIPE_SPEED  # Move pipe to the left

    # Remove pipes that go off the screen
    if pipes and pipes[0][0] < -10:
        pipes.pop(0)
        score += 1  # Increase score when a pipe is passed

# Function to draw everything on the display
def draw_game():
    display.fill(0)  # Clear the display

    # Draw bird
    display.pixel(BIRD_X, int(bird_y), (255, 255, 0))  # Yellow bird

    # Draw pipes
    for pipe in pipes:
        pipe_x, gap_y = pipe
        for y in range(64):  # Full height of the display
            if y < gap_y or y > gap_y + PIPE_GAP:  # Draw the pipe
                display.pixel(pipe_x, y, (0, 255, 0))  # Green pipes

    # Show the updated display
    display.show()

# Function to check for collisions
def check_collision():
    for pipe in pipes:
        pipe_x, gap_y = pipe
        if BIRD_X == pipe_x:
            if bird_y < gap_y or bird_y > gap_y + PIPE_GAP:
                return True  # Collision detected
    return False

# Main game loop
last_pipe_time = time.monotonic()

while True:
    # Get the current sound level
    sound_level = get_smoothed_sound_level()

    # Detect clap (flap)
    if sound_level > CLAP_THRESHOLD:
        current_time = time.monotonic()
        if current_time - last_clap_time > CLAP_TIMEOUT:
            bird_velocity = FLAP_STRENGTH  # Flap (jump up)
            last_clap_time = current_time

    # Update the bird's position
    update_bird()

    # Update the pipes
    update_pipes()

    # Generate new pipes at intervals
    if time.monotonic() - last_pipe_time > 2:  # Add a new pipe every 2 seconds
        generate_pipe()
        last_pipe_time = time.monotonic()

    # Draw the game
    draw_game()

    # Check for collisions
    if check_collision():
        print(f"Game Over! Your score: {score}")
        break  # End the game

    # Delay for a short period to control the game speed
    time.sleep(0.05)
