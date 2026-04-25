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

def find_portenta():
    ports = list_ports.comports()

    for port in ports:
        print(port.device, port.description, port.manufacturer, port.vid)
        if port.vid and port.vid == 0x2341:
            return port.device

    return None

class State(Enum):
    DEADZONE = "deadzone"
    VALID = "valid"

class WalkerBot:
    def __init__(self, angle_window=10, dist_window=5):
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

        self.w = 0
        self.v = 0

    def run(self):
        if self.ser is None:
            raise RuntimeError("Serial not initialized")

        print("Bot running...")

        while True:
            data = self._read_serial()
            if data is None:
                continue

            raw_dist, raw_angle = data
            self._update_filters(raw_dist, raw_angle)
            self._update_state()

            if self.current_state == State.DEADZONE:
                self._behavior_deadzone()

            elif self.current_state == State.VALID:
                self._behavior_valid()

            time.sleep(0.01)

    def _read_serial(self):
        if not self.ser or self.ser.in_waiting == 0:
            return None

        try:
            line = self.ser.readline().decode("utf-8").strip()
            if not line:
                return None

            dist, angle = map(float, line.split(","))
            return dist, angle

        except (ValueError, UnicodeDecodeError):
            return None

    def _update_filters(self, raw_dist, raw_angle):
        self.dist_window.append(raw_dist)
        self.angle_window.append(raw_angle)

        self.dist = sum(self.dist_window) / len(self.dist_window)
        self.angle = sum(self.angle_window) / len(self.angle_window)

    def _update_state(self):
        if abs(self.angle) > VALID_ANGLE_THRESHOLD:
            self.current_state = State.DEADZONE
        else:
            self.current_state = State.VALID

    def _behavior_deadzone(self):
        print("Deadzone: spinning")
        self.walker_controller.drive(w=self.DEADZONE_SPIN_W, v=0)

    def _behavior_valid(self):
        start_dist = self.dist
        # move forward to determine whether the stella is in front or behind
        self.walker_controller.drive(w=0, v=0.2)
        time.sleep(1)
        self.walker_controller.drive(w=0, v=0)
        if start_dist < self.dist: 
            print("Confirmed Stella in front!")
            self._behavior_forward()
        else:
            print("Stella behind, now spinning")
            self.spin_180() #spin 180; deadzone to non-deadzone

    def spin_180(self):
        """"""
        print("spinning 180")
        self._behavior_deadzone() # placeholder?

    def _behavior_forward(self):
        self.w = np.clip(self.angle * self.KP, -self.WMAX, self.WMAX)
        self.v = np.clip(np.cos(self.angle) * self.dist, -self.VMAX, self.VMAX)

        if self.dist < THRESHOLD_DIST: # if im already there
            self.w = 0
            self.v = 0

        self.walker_controller.drive(self.w, self.v)
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
