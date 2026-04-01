import pyvesc
from pyvesc import VESC
from pyvesc.VESC.messages.setters import SetDutyCycle
import serial
import time
from pynput import keyboard
import pyvesc.protocol.interface as v_interface 
import os

CAN_ID = 45
SPEED = 0.2
DURATION = 2
SERIAL_PORT = '/dev/ttyACM0'


def dual_drive_forward(motor, duration):
    start_time = time.time()
    print("Driving Both Wheels Forward")

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

def dual_drive_backward(motor, duration):
    start_time = time.time()
    print("Driving Both Wheels Backward")

    #while loop to incorporate duration
    while time.time() - start_time < duration:
        # Drive Main Motor
        motor.set_duty_cycle(-SPEED)

        # Send Message to Drive Secondary Motor
        msg_motor_2 = SetDutyCycle(-SPEED)
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

def turn_left(motor, duration):
    start_time = time.time()
    print("Turning Left")

    #while loop to incorporate duration
    while time.time() - start_time < duration:
        # Drive Main Motor
        motor.set_duty_cycle(-SPEED)

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

def turn_right(motor, duration):
    start_time = time.time()
    print("Turning Right")

    #while loop to incorporate duration
    while time.time() - start_time < duration:
        # Drive Main Motor
        motor.set_duty_cycle(SPEED)

        # Send Message to Drive Secondary Motor
        msg_motor_2 = SetDutyCycle(-SPEED)
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

def robust_init(port):
    ser = serial.Serial(port, 115200, timeout=0.1)
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    time.sleep(0.5)

def on_press(key, motor, duration):
    try:
        if key == keyboard.Key.right:
            dual_drive_forward(motor,duration)
        elif key == keyboard.Key.left:
            dual_drive_backward(motor,duration)
        elif key == keyboard.Key.up:
            turn_left(motor,duration)
        elif key == keyboard.Key.down:
            turn_right(motor,duration)
        elif key == keyboard.Key.space:
            motor.set_duty_cycle(0)
        elif key == keyboard.Key.esc:
            # Stop the listener
            return False
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # # Manually open and clear the port before giving it to PyVESC
    # temp_ser = serial.Serial(SERIAL_PORT, baudrate=115200, timeout=0.5)
    # temp_ser.reset_input_buffer()
    # temp_ser.reset_output_buffer()
    # temp_ser.close() 
    # time.sleep(1) # Give the OS a moment to release the port
    # except Exception as e:
    #     print(f"Port reset failed: {e}")

    robust_init(SERIAL_PORT)

    try:
        with VESC(serial_port=SERIAL_PORT) as motor:
                   # Use a listener to monitor key presses
            with keyboard.Listener(on_press=lambda k: on_press(k, motor,DURATION)) as listener:
                listener.join()
    except Exception as e:
        robust_init(SERIAL_PORT)
 


        