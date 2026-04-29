import pyvesc
from pyvesc import VESC
from pyvesc.VESC.messages.setters import SetDutyCycle
from pyvesc.VESC.messages.setters import SetRPM
import serial
import time
import pyvesc.protocol.interface as v_interface 
import os
from serial.tools import list_ports

CAN_ID = 45
# moved serial port definition to main loop

FULL_CIRC = 59.69 
WHEEL_CIRC = 18.8
FULL_ROT = FULL_CIRC/WHEEL_CIRC
RPM = 200

def find_vesc():
    ports = list_ports.comports()

    for port in ports:
        print(port.device, port.description, port.manufacturer, port.vid)
        # figure out what the vesc actually says, i just did not the arduino for now
        if port.manufacturer and "Arduino" not in port.manufacturer: 
            return port.device
        
    return None

def duration_calc():
    angle = int(input("Input Angle to Move:"))
    duration = (angle / 360) * FULL_ROT * (1/RPM) * 60
    
    return duration


def turn_right(motor, duration):
    start_time = time.time()
    print("Turning Right: Left Wheel CW, Right Wheel CeddCW")

    #while loop to incorporate duration
    while time.time() - start_time < duration:
        # Drive Main Motor
        motor.set_rpm(-RPM)

        # Send Message to Drive Secondary Motor
        msg_motor_2 = SetRPM(RPM)
        msg_motor_2.can_id = CAN_ID  # The ID of your second motor
        packet = v_interface.encode(msg_motor_2)
        motor.write(packet)

    time.sleep(0.1)

    #Stop Motors after duration done
    print("Duration reached. Stopping motors.")
    motor.set_rpm(0)
    
    stop_msg = SetRPM(0)
    stop_msg.can_id = CAN_ID
    motor.write(v_interface.encode(stop_msg))




if __name__ == '__main__':
    SERIAL_PORT = find_vesc()
    if SERIAL_PORT is None:
        print("No VESC found. Exiting.")
        exit(1)
    with VESC(serial_port=SERIAL_PORT) as motor:
        #duration = duration_calc()
        #print(f"Duration: {duration} seconds")
        
        #turn_right(motor,duration)

            msg_motor_2 = SetRPM(RPM)
            msg_motor_2.can_id = CAN_ID  # The ID of your second motor
            packet = v_interface.encode(msg_motor_2)
            motor.write(packet)

