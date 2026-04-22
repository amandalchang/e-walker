import serial
import time
from enum import Enum
from collections import deque

port = "/dev/ttyACM0"
baud_rate = 115200

TURN_VAL = 5
THRESHOLD_DIST = 20
VALID_VAL = 45

class State(Enum):
    RIGHT = "right"
    LEFT = "left"
    FORWARD = "forward"
    BACKWARD = "backward"
    STOP = "stop"

class WalkerBot:
    def __init__(self, angle_window=10, dist_window=10):
        self.current_state = State.STOP
        self.angle = 0
        self.dist = 0
        self.angle_window = deque(maxlen=angle_window)
        self.dist_window = deque(maxlen=dist_window)
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
        original_dist = self.dist
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
            if self.get_filtered_portenta():
                print(f"dist={self.dist:.1f}, angle={self.angle:.1f}")

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
            else:
                self.current_state = State.STOP
            time.sleep(0.02)

    def _read_serial(self):
        """Bridge between the Portenta and your logic."""
        if not self.ser or self.ser.in_waiting == 0:
            return None
        try:
            line = self.ser.readline().decode("utf-8").strip()
            if not line:
                return None
            parts = line.split(",")
            if len(parts) != 2:
                return None
            dist = float(parts[0])
            angle = float(parts[1])
            return dist, angle
        except (ValueError, UnicodeDecodeError):
            print("Skipping bad data")
            return None

    
    def get_filtered_portenta(self):
        data = self._read_serial()
        if data is None:
            return False
        raw_dist, raw_angle = data

        if abs(raw_angle) > VALID_VAL:
            return False

        self.dist_window.append(raw_dist)
        self.angle_window.append(raw_angle)

        if len(self.dist_window) == 0 or len(self.angle_window) == 0:
            return False

        self.dist = sum(self.dist_window) / len(self.dist_window)
        self.angle = sum(self.angle_window) / len(self.angle_window)

        return True

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
