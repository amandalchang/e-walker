from pyvesc import VESC
from pyvesc.VESC.messages.setters import SetDutyCycle
import serial
import time
from pynput import keyboard

CAN_ID = 45

# Initialize your serial connection to the "Master" VESC
serial_port = '/dev/ttyACM0' 

duration = 2

if __name__ == '__main__':
    with VESC(serial_port=serial_port) as main:

        # Control Motor 1 (Local/Master)
        # This sends the command directly to ID 1
        main.set_duty_cycle(0.2)
        time.sleep(duration)
        main.set_duty_cycle(0)

        # # Control Motor 2 (Remote/Slave via CAN)
        # # We create a message and specify the target CAN ID
        # msg_motor_2 = SetDutyCycle(duty_cycle=0.2)
        # msg_motor_2.can_id = 45  # The ID of your second motor
        # time.sleep(duration)
        # msg_motor_2 = SetDutyCycle(duty_cycle=0)
    
        # # Send the encoded packet through the master
        # master.write(master.encode(msg_motor_2))


