import serial
from serial.tools import list_ports
from pyvesc import VESC
import pyvesc.protocol.interface as v_interface 
from pyvesc.VESC.messages.setters import Alive, SetRPM
from math import pi
import time
import numpy as np

# WalkerController.control_velocity(v, w)
# Left motor is secondary and gets communicated to over CAN

class WalkerController():
    wheel_diameter = 0.16 # m
    wheelbase = 0.57 # m
    can_id = 45 # the ID of the second motor
    #can_id = 37 # CAN ID if USB cable connected to left motor
    left_adjust = 1.015

    def __init__(self):
        self.serial_port = self.find_vesc()
        self.VMAX = 2
        self.WMAX = 3

        if self.serial_port is None:
            print("No VESC found. Exiting.")
            return
        print(f"serial port: {self.serial_port}")
        self.vesc = VESC(serial_port=self.serial_port)
  
        
    def find_vesc(self):
        ports = list_ports.comports()

        for port in ports:
            print(port.device, port.description, port.manufacturer, port.vid)
            # figure out what the vesc actually says, i just did not the arduino for now
            if port.manufacturer and "Arduino" not in port.manufacturer: 
                print(f"I'm in: {port.description}")
                return port.device
            
        return None

    def send_CAN(self, rpm: int) -> None:
        msg_left_motor = SetRPM(rpm)
        msg_left_motor.can_id = self.can_id 
        packet = v_interface.encode(msg_left_motor)
        self.vesc.write(packet)

    def send_heartbeat(self, interval):
        #self.vesc.alive_msg()
        packet = v_interface.encode(Alive())
        self.vesc.write(packet)
        print("heartbeat")


    def set_right_motor_RPM(self, rpm: int) -> None:
        self.vesc.set_rpm(-rpm)
    
    def set_left_motor_RPM(self, rpm: int) -> None:
        self.send_CAN(rpm)

    def set_motor_RPMs(self, r: int, l: int) -> None:
        self.set_right_motor_RPM(r)
        self.set_left_motor_RPM(l)
    
    def drive(self, w: float, v: float, PRINT_ONLY=False) -> None:
        w = np.clip(w, -self.WMAX, self.WMAX)
        v = np.clip(v, -self.VMAX, self.VMAX)
        # Calculate wheel linear speeds
        right_speed = v + w * self.wheelbase / 2
        left_speed = v - w * self.wheelbase / 2

        # Calculate wheel RPM
        right_rpm = round(right_speed / self.wheel_diameter * pi * 60)
        left_rpm = round(self.left_adjust * left_speed / self.wheel_diameter * pi * 60)

        # print(f"right rpm: {right_rpm}, left rpm: {left_rpm}")

        if not PRINT_ONLY: 
            self.set_motor_RPMs(right_rpm, left_rpm)
            # print("Actually running")
            # print(f"Right RPM: {right_rpm}")
            # print(f"Left RPM: {left_rpm}")



    def close(self):
        self.vesc.stop_heartbeat()

def repeat_drive(w, v):
    walker_controller.drive(w, v)
    time.sleep(0.5)

if __name__ == "__main__":
    last_heartbeat = 0
    interval = 0.2
    walker_controller = WalkerController()
    # while True:
    #     current_time = time.time()

    #     if current_time - last_heartbeat >= interval:
    #         walker_controller.send_heartbeat(interval)
    #         last_heartbeat = current_time

    # for i in range(4):
    #     repeat_drive(4, 0) 
    # -1.3 and 0.2 spin it in a nice circle w,v 1.3, -0.2
    # -1.6 & -0.3
    for i in range(3): # 5 seconds at 2 is a full rotation
        repeat_drive(0, 0.7)
    # for i in range(10): # 5 seconds at 2 is a full rotation
    #     repeat_drive(0, -0.3)
    print("stop")
    walker_controller.drive(0, 0)

    walker_controller.close()
    

