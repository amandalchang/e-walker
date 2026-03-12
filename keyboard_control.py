import keyboard 
from pyvesc import VESC
import serial
import time



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



if __name__ == '__main__':
    with VESC(serial_port=serial_port) as motor:
        keyboard.add_hotkey('right', drive_forward(motor))
        keyboard.add_hotkey('left', drive_backward(motor))
        keyboard.add_hotkey('space', lambda: motor.set_duty_cycle(0))
        keyboard.wait("esc")
