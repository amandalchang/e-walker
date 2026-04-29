import serial
from serial.tools import list_ports
from pyvesc import VESC
import pyvesc.protocol.interface as v_interface 
from pyvesc.VESC.messages.setters import SetRPM
from math import pi
import time

# WalkerController.control_velocity(v, w)

class WalkerController():
    wheel_diameter = 0.16 # m
    wheelbase = 0.57 # m
    can_id = 45 # the ID of the second motor
    #can_id = 37 # CAN ID if USB cable connected to left motor

    def __init__(self):
        self.serial_port = self.find_vesc()

        if self.serial_port is None:
            print("No VESC found. Exiting.")
            return

        self.vesc = VESC(serial_port=self.serial_port)
  
        
    def find_vesc(self):
        ports = list_ports.comports()

        for port in ports:
            print(port.device, port.description, port.manufacturer, port.vid)
            # figure out what the vesc actually says, i just did not the arduino for now
            if port.manufacturer and "Arduino" not in port.manufacturer: 
                return port.device
            
        return None

    def send_CAN(self, rpm: int) -> None:
        msg_motor_2 = SetRPM(rpm)
        msg_motor_2.can_id = self.can_id 
        packet = v_interface.encode(msg_motor_2)
        self.vesc.write(packet)

    def send_heartbeat(self, interval):
        self.vesc.alive_msg()

    def set_right_motor_RPM(self, rpm: int) -> None:
        self.vesc.set_rpm(-rpm)
    
    def set_left_motor_RPM(self, rpm: int) -> None:
        self.send_CAN(rpm)

    def set_motor_RPMs(self, r: int, l: int) -> None:
        self.set_right_motor_RPM(r)
        self.set_left_motor_RPM(l)
    
    def drive(self, w: float, v: float, PRINT_ONLY=False) -> None:
        # Calculate wheel linear speeds
        right_speed = v + w * self.wheelbase / 2
        left_speed = v - w * self.wheelbase / 2

        # Calculate wheel RPM
        right_rpm = round(right_speed / self.wheel_diameter * pi * 60)
        left_rpm = round(left_speed / self.wheel_diameter * pi * 60)

        print(f"right rpm: {right_rpm}, left rpm: {left_rpm}")

        if not PRINT_ONLY: 
            self.set_motor_RPMs(right_rpm, left_rpm)
            print("Actually running")
            print(f"Right RPM: {right_rpm}")
            print(f"Left RPM: {left_rpm}")



    def close(self):
        self.vesc.stop_heartbeat()


if __name__ == "__main__":
    last_heartbeat = 0
    interval = 0.2
    walker_controller = WalkerController()
    while True:
        current_time = time.time()

        if current_time - last_heartbeat >= interval:
            walker_controller.send_heartbeat(interval)
            last_heartbeat = current_time


        # walker_controller.drive(0, 0.2)
        # time.sleep(2)
        # print("stop")
    
        # walker_controller.drive(0, 0)
    # time.sleep(2)
    # walker_controller.drive(0, -0.4)
    # time.sleep(3)

    # walker_controller.set_motor_RPMs(0, -300)
    # time.sleep(1)
    # walker_controller.set_motor_RPMs(0, 0)
    # walker_controller.close()

