import pyvesc
from pyvesc import VESC
from pyvesc.VESC.messages.setters import SetDutyCycle
from pyvesc.VESC.messages.setters import SetRPM
import serial
import time
from pynput import keyboard
import pyvesc.protocol.interface as v_interface 
import os

CAN_ID = 45
SPEED = -0.2 # negative to that positive SPEED is clockwise 
RPM = 5000
DURATION = 3
SERIAL_PORT = '/dev/ttyACM0'


def drive_forward(motor,duration):
    print("forward")
    motor.set_duty_cycle(0.1)
    time.sleep(duration)
    motor.set_duty_cycle(0)

def dual_drive_forward(motor, duration):
    start_time = time.time()
    print("Going Forward: Right Wheel CW, Left Wheel CCW")

    #while loop to incorporate duration
    while time.time() - start_time < duration:
        # Drive Main Motor
        #motor.set_duty_cycle(SPEED)
        motor.set_rpm(RPM)


        # Send Message to Drive Secondary Motor
        #msg_motor_2 = SetDutyCycle(-SPEED)
        msg_motor_2 = SetRPM(-RPM)
        msg_motor_2.can_id = CAN_ID  # The ID of your second motor
        packet = v_interface.encode(msg_motor_2)
        motor.write(packet)

    time.sleep(0.1)

    #Stop Motors after duration done
    print("Duration reached. Stopping motors.")
    #motor.set_duty_cycle(0)
    motor.set_rpm(0)

    
    #stop_msg = SetDutyCycle(0)
    stop_msg = SetRPM(0)
    stop_msg.can_id = CAN_ID
    motor.write(v_interface.encode(stop_msg))

def dual_drive_backward(motor, duration):
    start_time = time.time()
    print("Going Backward: Right Wheel CCW, Left Wheel CW")

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

def turn_left(motor, duration):
    start_time = time.time()
    print("Turning Left: Left Wheel CCW, Right Wheel CW")

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



def robust_init(port):
    ser = serial.Serial(port, 115200, timeout=0.1)
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    time.sleep(1)

def on_press(key, motor, duration):
    try:
        if key == keyboard.Key.right:
            #dual_drive_forward(motor,duration)
            drive_forward(motor,duration)
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


def on_release(key, motor):
    # When you let go of Right or Left, stop the motor
    if key == keyboard.Key.right or key == keyboard.Key.left:
        motor.set_duty_cycle(0)
    
    # Still use Esc to quit the whole script
    if key == keyboard.Key.esc:
        motor.set_duty_cycle(0) # Safety stop
        return False



if __name__ == '__main__':
    robust_init(SERIAL_PORT)
    
    with VESC(serial_port=SERIAL_PORT) as motor:
        print("Right - Forward. Left - Backward. Up - Turn Right. Down - Turn Left. Esc to quit.")
        
        # We now pass TWO functions to the listener
        with keyboard.Listener(
            on_press=lambda k: on_press(k, motor,DURATION),
        ) as listener:
            listener.join()



# if __name__ == '__main__':

#     robust_init(SERIAL_PORT)

#     try:
#         with VESC(serial_port=SERIAL_PORT) as motor:
#                    # Use a listener to monitor key presses
#             with keyboard.Listener(on_press=lambda k: on_press(k, motor,DURATION)) as listener:
#                 listener.join()
#     except Exception as e:
#         robust_init(SERIAL_PORT)
 
  