import pyvesc
from pyvesc import VESC
from pyvesc.VESC.messages.setters import SetDutyCycle
import serial
import time
from pynput import keyboard
import pyvesc.protocol.interface as v_interface  

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
        msg_motor_2 = SetDutyCycle(duty_cycle=0.1)
        msg_motor_2.can_id = 45  # The ID of your second motor
        # time.sleep(duration)
        #msg_motor_2 = SetDutyCycle(duty_cycle=0)
    

        packet = v_interface.encode(msg_motor_2)
        # # Send the encoded packet through the master
        main.write(packet)



# import serial
# import time
# from pyvesc import VESC
# from pyvesc.VESC.messages.setters import SetDutyCycle

# # 1. Setup the connection
# # Make sure this matches the port you found earlier!
# serial_port = '/dev/ttyACM0' 

# try:
#     with VESC(serial_port=serial_port) as master:
#         print("Connected to Master VESC")

#         # --- CONTROL MOTOR 1 (Local) ---
#         # The library has a built-in helper for the local motor
#         master.set_duty_cycle(0.1) 
        
#         # --- CONTROL MOTOR 2 (Over CAN) ---
#         # For the second motor, we create the message manually
#         # and assign the CAN ID (Usually 2, if you set it in VESC Tool)
#         msg_motor_2 = SetDutyCycle(duty_cycle=0.1)
#         msg_motor_2.can_id = 2 
        
#         # We tell the Master to encode and send this over the wire
#         master.write(master.encode(msg_motor_2))
        
#         print("Commands sent to both motors.")
#         time.sleep(2)
        
#         # Stop both
#         master.set_duty_cycle(0)
#         stop_m2 = SetDutyCycle(duty_cycle=0)
#         stop_m2.can_id = 2
#         master.write(master.encode(stop_m2))

# except Exception as e:
#     print(f"Error: {e}")