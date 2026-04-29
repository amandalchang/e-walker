import serial
import time
import numpy as np
from enum import Enum
from collections import deque
from serial.tools import list_ports
from motor_firmware.walker_controller import WalkerController

baud_rate = 115200

TURN_VAL = 5
THRESHOLD_DIST = 20
VALID_ANGLE_THRESHOLD = 45
DEBUG = True
PRINT_ONLY = True
ERR_VAL = 400
ANGLE_MONITOR = False

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
    def __init__(self, angle_window=3, dist_window=2):
        self.current_state = State.DEADZONE

        self.angle_window = deque(maxlen=angle_window)
        self.dist_window = deque(maxlen=dist_window)

        self.angle = 0
        self.dist = 0

        self.ser = None
        self.walker_controller = WalkerController()

        self.KP = 10
        self.WMAX = 0.6
        self.VMAX = 0.6
        self.DEADZONE_SPIN_W = 0.2

        self.state_streak = 0
        self.STATE_CONFIRM_COUNT = 3

        self.prev_dist = None
        self.dist_delta_window = deque(maxlen=5)

        self.w = 0
        self.v = 0

    def run(self):
        if self.ser is None:
            raise RuntimeError("Serial not initialized")

        print("Bot running...")

        while True:
            data = self._read_serial()
            if data:
                self._update_filters(*data)
                self._update_state()

                if self.current_state == State.DEADZONE:
                    self._behavior_deadzone()

                elif self.current_state == State.VALID:
                    self._behavior_valid()

    def _read_serial(self):
        if not self.ser or self.ser.in_waiting == 0:
            return None

        try:
            line = self.ser.readline().decode("utf-8").strip()
            if not line:
                return None

            dist, angle = map(float, line.split(","))
            if DEBUG:
                print(f"Raw Dist: {dist}, Raw Angle: {angle}")
            return dist, angle

        except (ValueError, UnicodeDecodeError):
            return None

    def _update_filters(self, raw_dist: float, raw_angle: float):
        self.dist_window.append(raw_dist)
        if abs(raw_angle) < VALID_ANGLE_THRESHOLD:
            self.angle_window.append(raw_angle)

        if len(self.angle_window) == 0:
            self.angle = ERR_VAL
        else:
            self.angle = np.median(list(self.angle_window))

        self.dist = np.median(list(self.dist_window))
        
        if ANGLE_MONITOR:
            print(f"ANGLE LIST: {list(self.angle_window)}")

        if DEBUG | ANGLE_MONITOR:
            print(f"Dist: {self.dist}, Angle: {self.angle}")

    def _update_state(self):
        new_state = State.DEADZONE if self.angle == ERR_VAL else State.VALID
        if DEBUG: print("New State: " + new_state.name)
        if new_state == self.current_state:
            self.state_streak = 0
        else:
            self.state_streak += 1
            if self.state_streak >= self.STATE_CONFIRM_COUNT:
                self.current_state = new_state
                self.state_streak = 0

    def _behavior_deadzone(self):
        if DEBUG: print("Deadzone: spinning")
        self.walker_controller.drive(w=self.DEADZONE_SPIN_W, v=0, PRINT_ONLY=PRINT_ONLY)

    # def _behavior_valid(self):
    #     if DEBUG: print("start valid behavior")
    #     start_dist = self.dist
    #     # move forward to determine whether the stella is in front or behind
    #     self.walker_controller.drive(w=0, v=0.2, PRINT_ONLY=PRINT_ONLY)
    #     time.sleep(1)
    #     self.walker_controller.drive(w=0, v=0, PRINT_ONLY=PRINT_ONLY)
    #     self.ser.reset_input_buffer()
    #     for _ in range(3):
    #         data = self._read_serial()
    #         if data: self._update_filters(*data)
    #         time.sleep(2)
        
    #     if start_dist > self.dist: 
    #         if DEBUG: print("Confirmed Stella in front!")
    #         self._behavior_forward()
    #     else:
    #         if DEBUG: print("Stella behind, now spinning")
    #         self.spin_180() #spin 180; deadzone to non-deadzone
    def _behavior_valid(self):
        if self.prev_dist is not None:
            self.dist_delta_window.append(self.dist - self.prev_dist)
            print(self.dist - self.prev_dist)
        self.prev_dist = self.dist

        # need a full window before making a decision
        if len(self.dist_delta_window) < self.dist_delta_window.maxlen:
            print("Getting full window")
            self.walker_controller.drive(w=0, v=0, PRINT_ONLY=PRINT_ONLY)
            return

        avg_delta = np.median(list(self.dist_delta_window))

        if avg_delta < 0:  # distance shrinking — target approaching or we're approaching target
            self._behavior_forward()
            print("foward behavior")
        elif avg_delta > 2:  # distance growing with hysteresis band
            self.spin_180()
            print("spin behavior")
        else:  # roughly stable distance — just hold
            print(self.dist - self.prev_dist)
            self.walker_controller.drive(w=0, v=0, PRINT_ONLY=PRINT_ONLY)
            print("stable distance")

    def spin_180(self):
        """"""
        if DEBUG: print("spinning 180")
        self._behavior_deadzone() # placeholder?

    def _behavior_forward(self):
        if DEBUG: print("starting forward behavior")
        angle_rad = np.radians(self.angle)
        self.w = np.clip(angle_rad * self.KP, -self.WMAX, self.WMAX)
        self.v = np.clip(np.cos(angle_rad) * self.dist, -self.VMAX, self.VMAX)

        if self.dist < THRESHOLD_DIST: # if im already there
            self.w = 0
            self.v = 0

        self.walker_controller.drive(self.w, self.v, PRINT_ONLY)
        print(f"Driving: w={self.w:.2f}, v={self.v:.2f}")

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
