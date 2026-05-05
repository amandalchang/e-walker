import serial
import time
import numpy as np
from enum import Enum
from collections import deque
from serial.tools import list_ports
from walker_controller import WalkerController

baud_rate = 115200

TURN_VAL = 5
THRESHOLD_DIST = 100
VALID_ANGLE_THRESHOLD = 45
DEBUG = False
PRINT_ONLY = False
ERR_VAL = 400
ANGLE_MONITOR = True
PRINT_VELOCITIES = False

# TODO: spin 180 in the direction you came from

def find_portenta():
    ports = list_ports.comports()

    for port in ports:
        print(port.device, port.description, port.manufacturer, port.vid)
        if port.description and "Portenta" in port.description:
            print(f"Connecting to {port.description}") 
            return port.device

    return None

class State(Enum):
    DEADZONE = "deadzone"
    VALID = "valid"

class WalkerBot:
    def __init__(self, angle_window=5, dist_window=2):
        self.current_state = State.DEADZONE

        self.angle_window = deque(maxlen=angle_window)
        self.dist_window = deque(maxlen=dist_window)

        self.angle = 0
        self.dist = 0

        self.ser = None
        self.walker_controller = WalkerController()

        self.KW = 1.4
        self.KV = 0.0035
        self.WMAX = 2
        self.VMAX = 1
        self.DEADZONE_SPIN_W = -1.3
        self.DEADZONE_SPIN_V = 0.2

        self.state_streak = 2
        self.STATE_CONFIRM_COUNT = 2

        self.prev_dist = None
        self.dist_delta_window = deque(maxlen=5)

        self.w = 0
        self.v = 0

        self.start = True

    def run(self):
        if self.ser is None:
            raise RuntimeError("Serial not initialized")

        print("Walker start...")

        while True:
            data = self._read_serial()
            if data:
                self._update_filters(*data)
                self._update_state()

                if self.current_state == State.DEADZONE:
                    print("deadzone")
                    #self.walker_controller.drive(0, 0, PRINT_ONLY=PRINT_ONLY)
                    self._behavior_deadzone()

                elif self.current_state == State.VALID:
                    # if self.start:
                    #     self.walker_controller.drive(w=0, v=0.1, PRINT_ONLY=PRINT_ONLY)
                    #     self.start = False
                    self._behavior_valid()

    def _read_serial(self):
        if not self.ser or self.ser.in_waiting == 0:
            return None

        try:
            line = self.ser.readline().decode("utf-8").strip()
            if not line:
                return None

            dist, angle = map(float, line.split(","))
            if ANGLE_MONITOR:
                print(f"Raw Dist: {dist}, Raw Angle: {angle}")
            return dist, angle

        except (ValueError, UnicodeDecodeError):
            return None

    def _update_filters(self, raw_dist: float, raw_angle: float):
        self.dist_window.append(raw_dist)
        if abs(raw_angle) < VALID_ANGLE_THRESHOLD:
            self.angle_window.append(raw_angle)
        else:
            self.angle_window.clear()

        if len(self.angle_window) == 0:
            self.angle = ERR_VAL
        else:
            self.angle = np.median(list(self.angle_window))

        self.dist = np.median(list(self.dist_window))
        
        # if ANGLE_MONITOR:
        #     print(f"ANGLE LIST: {list(self.angle_window)}")

        if DEBUG | ANGLE_MONITOR:
            print(f"Dist: {self.dist}, Angle: {self.angle}")

    def _update_state(self):
        new_state = State.DEADZONE if self.angle == ERR_VAL else State.VALID
        if new_state == self.current_state:
            self.state_streak = 0
        else:
            self.state_streak += 1
            if self.state_streak >= self.STATE_CONFIRM_COUNT:
                if new_state == State.DEADZONE:
                    self.dist_delta_window.clear()
                    self.prev_dist = None
                self.current_state = new_state
                self.state_streak = 0

    def _behavior_deadzone(self):
        if DEBUG: print("deadzone behavior")
        self.w = 0 if self.dist < THRESHOLD_DIST else self.DEADZONE_SPIN_W
        self.v = 0 if self.dist < THRESHOLD_DIST else self.DEADZONE_SPIN_V
        self.walker_controller.drive(self.w, self.v, PRINT_ONLY=PRINT_ONLY)

    def _behavior_valid(self):
        if self.prev_dist is not None:
            self.dist_delta_window.append(self.dist - self.prev_dist)
        self.prev_dist = self.dist

        if len(self.dist_delta_window) < self.dist_delta_window.maxlen:
            self.walker_controller.drive(w=0, v=0, PRINT_ONLY=PRINT_ONLY)
            return

        avg_delta = np.median(list(self.dist_delta_window))

        if avg_delta < -2:  # distance shrinking — target approaching or we're approaching target
            self._behavior_forward()
        elif avg_delta > 2:  # distance growing with hysteresis band
            self.spin_180()

    def spin_180(self):
        if DEBUG: print("spinning 180")
        self.w = 0 if self.dist < THRESHOLD_DIST else self.DEADZONE_SPIN_W
        self.v = 0 if self.dist < THRESHOLD_DIST else self.DEADZONE_SPIN_V
        self.walker_controller.drive(self.w, self.v, PRINT_ONLY=PRINT_ONLY)

    def _behavior_forward(self):
        if DEBUG: print(f"forward behavior, Dist: {self.dist}, Angle: {self.angle}")
        angle_rad = np.radians(self.angle)
        distance_error = self.dist - THRESHOLD_DIST
        self.v = np.clip(distance_error * self.KV, 0, self.VMAX)
        if self.angle != ERR_VAL:
            self.w = -np.clip(angle_rad * self.KW, -self.WMAX, self.WMAX)

        if self.dist < THRESHOLD_DIST: # if im already there
            print("target reached, stopping")
            self.w = 0
            self.v = 0

        self.walker_controller.drive(self.w, self.v, PRINT_ONLY)
        if self.w > 0: # TURNING LEFT
            print(f"Left: w={self.w:.2f}, v={self.v:.2f}")
        elif self.w < 0:
            print(f"Right : w={self.w:.2f}, v={self.v:.2f}")
        else:
            print(f"Forward: w={self.w:.2f}, v={self.v:.2f}")

if __name__ == "__main__":
    robot = WalkerBot()

    try:
        port = find_portenta()
        if port is None:
            raise RuntimeError("Portenta not found")

        robot.ser = serial.Serial(port, baud_rate, timeout=1)
        robot.ser.flush()

        print(f"Connected to {port}")
        robot.run()

    except KeyboardInterrupt:
        print("\nStopped by user")

    finally:
        if robot.ser:
            robot.ser.close()
