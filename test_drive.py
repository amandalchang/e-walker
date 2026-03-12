from pyvesc import VESC
import serial
import time

serial_port = '/dev/ttyACM0' #fix with actual serial port once tested on raspi 


## FROM EXAMPLE CODE FROM PYVESC GITHUB DOCUMENTATION
def run_motor_using_with():
    with VESC(serial_port=serial_port) as motor:
        print("Firmware: ", motor.get_firmware_version())
        motor.set_duty_cycle(.02)

        # run motor and print out rpm for ~2 seconds
        for i in range(15):
            time.sleep(0.1)
            print(motor.get_measurements().rpm)
        motor.set_rpm(0)



if __name__ == '__main__':
    run_motor_using_with()