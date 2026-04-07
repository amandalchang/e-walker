import pyvesc
from pyvesc import VESC
from pyvesc.VESC.messages.setters import SetDutyCycle
import serial
import time
import pyvesc.protocol.interface as v_interface 
import os

CAN_ID = 45
SERIAL_PORT = '/dev/ttyACM0'


FULL_CIRC = 59.69 
WHEEL_CIRC = 18.8
FULL_ROT = FULL_CIRC/WHEEL_CIRC
RPM = 56

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
        motor.set_duty_cycle(SPEED)

        # Send Message to Drive Secondary Motor
        msg_motor_2 = SetDutyCycle(SPEED)
        msg_motor_2.can_id = CAN_ID  # The ID of your second motor
        packet = v_interface.encode(msg_motor_2)
        motor.write(packet)

    time.sleep(0.1)

    #Stop Motors after duration done
    print("Duration reached. Stopping motors.")
    motor.set_duty_cycle(0)
    
    stop_msg = SetDutyCycle(0)
    stop_msg.can_id = CAN_ID
    motor.write(v_interface.encode(stop_msg))




if __name__ == '__main__':

    with VESC(serial_port=SERIAL_PORT) as motor:
        duration = duration_calc()
        print(f"Duration: {duration} seconds")
        
        turn_right(motor,duration)
