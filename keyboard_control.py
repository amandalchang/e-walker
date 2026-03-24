#import keyboard 
from pyvesc import VESC
import serial
import time
from pynput import keyboard



serial_port = '/dev/ttyACM0' #fix with actual serial port once tested on raspi 

duration = 2


def drive_forward(motor):
    print("forward")
    motor.set_duty_cycle(0.1)
    time.sleep(duration)
    motor.set_duty_cycle(0)

def drive_backward(motor):
    print("backward")
    motor.set_duty_cycle(-0.1)
    time.sleep(duration)
    motor.set_duty_cycle(0)

def on_press(key, motor):
    try:
        if key == keyboard.Key.right:
            drive_forward(motor)
        elif key == keyboard.Key.left:
            drive_backward(motor)
        elif key == keyboard.Key.space:
            motor.set_duty_cycle(0)
        elif key == keyboard.Key.esc:
            # Stop the listener
            return False
    except Exception as e:
        print(f"Error: {e}")

def continuous_forward(motor):
    print("continous forward")
    motor.set_duty_cycle(-0.1)

def continuous_backward(motor):
    print("continous backward")
    motor.set_duty_cycle(0.1)

def continuous_press(key, motor):
    try:
        if key == keyboard.Key.right:
            continuous_forward(motor)
        elif key == keyboard.Key.left:
            continuous_backward(motor)
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

# Used to have a continuous drive forward or backward until space is pressed
# if __name__ == '__main__':
#     with VESC(serial_port=serial_port) as motor:
#         print("Control active. Use Arrow Keys to drive, Space to stop, Esc to quit.")
        
#         # Use a listener to monitor key presses
#         with keyboard.Listener(on_press=lambda k: continuous_press(k, motor)) as listener:
#             listener.join()


# Trying to use keyboard library but you have to be on root for that so the following didnt work without other workarounds 
# if __name__ == '__main__':
#     with VESC(serial_port=serial_port) as motor:
#         keyboard.add_hotkey('right', drive_forward(motor))
#         keyboard.add_hotkey('left', drive_backward(motor))
#         keyboard.add_hotkey('space', lambda: motor.set_duty_cycle(0))
#         keyboard.wait("esc")



if __name__ == '__main__':
    with VESC(serial_port=serial_port) as motor:
        print("Holding Right/Left drives. Releasing stops. Esc to quit.")
        
        # We now pass TWO functions to the listener
        with keyboard.Listener(
            on_press=lambda k: on_press(k, motor),
            on_release=lambda k: on_release(k, motor)
        ) as listener:
            listener.join()