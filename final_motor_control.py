import pyvesc
from pyvesc import VESC
from pyvesc.VESC.messages.setters import SetDutyCycle
import serial
import time
from pynput import keyboard
import pyvesc.protocol.interface as v_interface 

CAN_ID = 45
SPEED = 

def dual_drive_forward(motor):
    print("Driving Both Wheels Forward")
    # Drive Main Motor
    motor.set_duty_cycle(SPEED)

    # Send Message to Drive Secondary Motor
    msg_motor_2 = SetDutyCycle(SPEED.2)
    msg_motor_2.can_id = CAN_ID  # The ID of your second motor
    packet = v_interface.encode(msg_motor_2)
    motor.write(packet)



if __name__ == '__main__':
    # Manually open and clear the port before giving it to PyVESC
    temp_ser = serial.Serial(serial_port, baudrate=115200, timeout=0.5)
    temp_ser.reset_input_buffer()
    temp_ser.reset_output_buffer()
    temp_ser.close() 
    time.sleep(0.5) # Give the OS a moment to release the port
    # ----------------


    with VESC(serial_port=serial_port) as main:
        dual_drive_forward(main)