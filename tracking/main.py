import serial
import time
from enum import Enum

port = "/dev/ttyACM0"
baud_rate = 115200

TURN_VAL = 10
THRESHOLD_DIST = 100
VALID_VAL = 45

class State(Enum):
    RIGHT = "right"
    LEFT = "left"
    FORWARD = "forward"
    BACKWARD = "backward"
    STOP = "stop"

class WalkerBot:
    def __init__(self):
        self.current_state = State.STOP
        self.angle = 0 #???
        self.dist = 0
        # Initialize serial later to handle errors
        self.ser = None 

    def move_robot(self):
        """Hardware execution based on the current state."""
        match self.current_state:
            case State.FORWARD:
                print("FORWARD")
            case State.BACKWARD:
                print("Beep beep: Reversing.")
            case State.LEFT | State.RIGHT:
                print(f"Turning {self.current_state.value}...")
            case State.STOP:
                print("Stop")
            case _:
                print("Unknown state detected.")

    def orient(self):
        # Using a list for avg logic as per your snippet
        original_dist = sum([self.dist]) / 1 # Simplified avg logic
        # drive_forward(duration)  <-- Ensure this is defined
        
        # current_distance assumed to be updated via serial
        if original_dist < self.dist: 
            self.drive()
        else:
            self.spin()

    def spin(self):
        while abs(self.angle) > VALID_VAL:
            # turn_right() <-- Ensure this hardware call is defined
            print("Spinning...")
            self.read_serial() # Important: Update values during loop
            
        # stop() 
        self.orient()
        
    def drive(self):
        while True:
            self.read_serial()
            if self.dist < THRESHOLD_DIST:
                self.current_state = State.STOP
            elif self.angle > TURN_VAL:
                self.current_state = State.RIGHT
            elif self.angle < -TURN_VAL:
                self.current_state = State.LEFT
            elif abs(self.angle) < TURN_VAL:
                self.current_state = State.FORWARD
            else:
                self.current_state = State.STOP
            
            self.move_robot()

    def read_serial(self):
        """Bridge between the Portenta and your logic."""
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').rstrip()
                if line:
                    parts = line.split(",")
                    print(parts)
                    if len(parts) == 2:
                        self.dist = float(parts[0])
                        self.angle = float(parts[1])
            except (ValueError, UnicodeDecodeError) as e:
                print(f"skipping bad data")
            return line
        return None
    
    def filter_portenta(self):

# --- Main Execution ---
if __name__ == "__main__":
    bot = WalkerBot()
    try:
        bot.ser = serial.Serial(port, baud_rate, timeout=1)
        bot.ser.flush()
        print(f"Connected to {port}.")
        
        bot.drive()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        if bot.ser:
            bot.ser.close()
