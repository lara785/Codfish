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
OBSTACLE_SPEED = 1
OBSTACLE_GAP = 12  # Vertical gap size for obstacles
BOAT_X = 20  # Boat's horizontal position (fixed)
OBSTACLE_INTERVAL = 40  # Distance between obstacles

# Game state variables
boat_y = 32  # Start the boat in the middle of the screen
boat_velocity = 0
obstacles = []  # List of obstacles (tuples of (x_position, gap_position))
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

# Function to generate a new obstacle (buoy)
def generate_obstacle():
    gap_y = random.randint(10, 64 - OBSTACLE_GAP - 10)  # Random vertical gap position
    obstacles.append([128, gap_y])  # New obstacle starts off-screen

# Function to update the boat's position
def update_boat():
    global boat_y, boat_velocity

    # Apply gravity (water buoyancy here)
    boat_velocity += GRAVITY
    boat_y += boat_velocity

    # Keep boat within bounds (within the water)
    if boat_y < 0:
        boat_y = 0
        boat_velocity = 0
    elif boat_y > 63:
        boat_y = 63
        boat_velocity = 0

# Function to move the obstacles and check for collisions
def update_obstacles():
    global score

    for obstacle in obstacles:
        obstacle[0] -= OBSTACLE_SPEED  # Move obstacle to the left

    # Remove obstacles that go off the screen
    if obstacles and obstacles[0][0] < -10:
        obstacles.pop(0)
        score += 1  # Increase score when an obstacle is passed

# Function to draw the boat and obstacles
def draw_game():
    display.fill(0)  # Clear the display

    # Draw boat (as a rectangle representing a boat)
    display.pixel(BOAT_X, int(boat_y), (0, 0, 255))  # Blue boat

    # Draw obstacles (buoys or pillars)
    for obstacle in obstacles:
        obstacle_x, gap_y = obstacle
        for y in range(64):  # Full height of the display
            if y < gap_y or y > gap_y + OBSTACLE_GAP:  # Draw the obstacle
                display.pixel(obstacle_x, y, (255, 0, 0))  # Red buoys

    # Show the updated display
    display.show()

# Function to check for collisions between the boat and obstacles
def check_collision():
    for obstacle in obstacles:
        obstacle_x, gap_y = obstacle
        if BOAT_X == obstacle_x:
            if boat_y < gap_y or boat_y > gap_y + OBSTACLE_GAP:
                return True  # Collision detected
    return False

# Main game loop
last_obstacle_time = time.monotonic()

while True:
    # Get the current sound level
    sound_level = get_smoothed_sound_level()

    # Detect clap (flap, or boat jumping up)
    if sound_level > CLAP_THRESHOLD:
        current_time = time.monotonic()
        if current_time - last_clap_time > CLAP_TIMEOUT:
            boat_velocity = FLAP_STRENGTH  # Flap (jump up)
            last_clap_time = current_time

    # Update the boat's position
    update_boat()

    # Update the obstacles
    update_obstacles()

    # Generate new obstacles at intervals
    if time.monotonic() - last_obstacle_time > 2:  # Add a new obstacle every 2 seconds
        generate_obstacle()
        last_obstacle_time = time.monotonic()

    # Draw the game
    draw_game()

    # Check for collisions
    if check_collision():
        print(f"Game Over! Your score: {score}")
        break  # End the game

    # Delay for a short period to control the game speed
    time.sleep(0.05)
