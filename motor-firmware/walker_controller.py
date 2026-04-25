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
            if port.vid and port.vid == 0x1155: 
                return port.device
            
        return None

    def set_right_motor_RPM(self, rpm: int) -> None:
        self.vesc.set_rpm(-rpm)
    
    def set_left_motor_RPM(self, rpm: int) -> None:
        msg_motor_2 = SetRPM(rpm)
        msg_motor_2.can_id = self.can_id 
        packet = v_interface.encode(msg_motor_2)
        self.vesc.write(packet)

    def set_motor_RPMs(self, r: int, l: int) -> None:
        self.set_right_motor_RPM(r)
        self.set_left_motor_RPM(l)
    
    def drive(self, w: float, v: float) -> None:
        # Calculate wheel linear speeds
        right_speed = v + w * self.wheelbase / 2
        left_speed = v - w * self.wheelbase / 2

        # Calculate wheel RPM
        right_rpm = round(right_speed / self.wheel_diameter * pi * 60)
        left_rpm = round(left_speed / self.wheel_diameter * pi * 60)

        print(right_rpm, left_rpm)

        self.set_motor_RPMs(right_rpm, left_rpm)

    def close(self):
        self.vesc.stop_heartbeat()


# if __name__ == "__main__":
#     walker_controller = WalkerController()

#     walker_controller.drive(0, 0.2)
#     time.sleep(1)
#     walker_controller.drive(0, 0)

#     # walker_controller.set_motor_RPMs(0, -300)
#     # time.sleep(1)
#     # walker_controller.set_motor_RPMs(0, 0)
#     walker_controller.close()

