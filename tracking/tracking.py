import serial
import time

print(serial.__file__)
print(f"Has readline: {hasattr(serial.Serial, 'readline')}")

port = "/dev/ttyACM1"
baud_rate = 115200
output_file = "serial_log.txt"

try:
    ser = serial.Serial(port, baud_rate, timeout=1)
    ser.flush()

    print(f"Connected to {port}. Logging data to {output_file}.")
    
    with open(output_file, "a") as file:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(line)
                file.write(line + "\n\n")
                file.flush()
except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"\nAn error occurred: {e}")
finally:
    if 'ser' in locals():
        ser.close()

from enum import Enum

class State(Enum):
    RIGHT = "right"
    LEFT = "left"
    FORWARD = "forward"
    BACKWARD = "backward"
    STOP = "stop"

current_state = STOP

def move_robot(current_state):
    match current_state:
        case State.FORWARD:
            print("Engaging motors: Moving straight ahead.")
        case State.BACKWARD:
            print("Beep beep: Reversing.")
        case State.LEFT | State.RIGHT:
            print(f"Turning {current_state.value}...")
        case State.STOP:
            print("All systems halted.")
        case _:
            print("Unknown state detected.")

move_robot(State.FORWARD)

TURN_VAL = 10
THRESHOLD_DIST = 10
VALID_VAL = 45

def orient():
    # call timed drive forward func
    original_dist = avg([dist])
    drive_forward(duration)

    if original_dist < current_distance:
        drive()
    else:
        spin()

def spin():
    while (abs(angle) > VALID_VAL):
        turn_right()
    stop()
    orient()
    
def drive():
    while(1):
        # assuming stella is in front of it
        if angle > TURN_VAL:
            current_state = RIGHT
        elif angle < -TURN_VAL:
            current_state = LEFT
        elif abs(angle) < TURN_VAL and dist < THRESHOLD_DIST:
            current_state = FORWARD
        else current_state = STOP
