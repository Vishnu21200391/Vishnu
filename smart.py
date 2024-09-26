import RPi.GPIO as GPIO
import time
import signal
import sys
from mfrc522 import SimpleMFRC522
from threading import Thread

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Servo motor setup
SERVO_PIN = 18  # Pin for controlling the servo motor
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM frequency
servo.start(0)

# Keypad setup (4x4 matrix keypad)
ROW_PINS = [5, 6, 13, 19]
COL_PINS = [12, 16, 20, 21]
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Initialize the GPIO pins for the keypad
for row_pin in ROW_PINS:
    GPIO.setup(row_pin, GPIO.OUT)
    GPIO.output(row_pin, GPIO.HIGH)
    
for col_pin in COL_PINS:
    GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# RFID setup
rfid_reader = SimpleMFRC522()

# Global variables
CORRECT_PIN = "1234"
AUTHORIZED_RFID_TAGS = [1234567890]  # List of authorized RFID tag IDs

# Functions for locking and unlocking
def unlock_door():
    print("Unlocking door...")
    servo.ChangeDutyCycle(7)  # Adjust this for servo angle (unlock)
    time.sleep(1)

def lock_door():
    print("Locking door...")
    servo.ChangeDutyCycle(2)  # Adjust this for servo angle (lock)
    time.sleep(1)

# Function to get input from the keypad
def get_keypad_input():
    input = ""
    while len(input) < 4:
        for i, row_pin in enumerate(ROW_PINS):
            GPIO.output(row_pin, GPIO.LOW)
            for j, col_pin in enumerate(COL_PINS):
                if GPIO.input(col_pin) == GPIO.HIGH:
                    print(KEYPAD[i][j])  # Output the key pressed
                    input += KEYPAD[i][j]
                    time.sleep(0.3)  # Debounce delay
            GPIO.output(row_pin, GPIO.HIGH)
    return input

# Function to read RFID
def read_rfid():
    try:
        print("Place your RFID card near the reader...")
        id, text = rfid_reader.read()
        return id
    except Exception as e:
        print("RFID error:", str(e))
        return None

# Function to handle the smart lock logic
def smart_lock():
    while True:
        print("Waiting for RFID authentication or keypad input...")

        # RFID check
        id = read_rfid()
        if id in AUTHORIZED_RFID_TAGS:
            print("RFID authorized. Unlocking door...")
            unlock_door()
            time.sleep(5)
            lock_door()
        else:
            print("Unauthorized RFID.")

        # Keypad input check
        print("Enter the PIN on the keypad:")
        pin = get_keypad_input()
        if pin == CORRECT_PIN:
            print("PIN correct. Unlocking door...")
            unlock_door()
            time.sleep(5)
            lock_door()
        else:
            print("Incorrect PIN. Try again.")

# Graceful exit
def exit_program(signal, frame):
    print("\nExiting the program...")
    GPIO.cleanup()
    servo.stop()
    sys.exit(0)

# Bind signal handler for program exit
signal.signal(signal.SIGINT, exit_program)

if __name__ == "__main__":
    try:
        smart_lock_thread = Thread(target=smart_lock)
        smart_lock_thread.start()
    except KeyboardInterrupt:
        exit_program(None, None)
