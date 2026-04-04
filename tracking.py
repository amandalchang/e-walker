import serial
import time

print(serial.__file__)
print(f"Has readline: {hasattr(serial.Serial, 'readline')}")

port = "/dev/ttyACM1"
baud_rate = 115200
output_file = "serial_log.txt"

try:
    ser = serial.Serial(port, baud_rate, timeout=1)
    ser.flush()

    print(f"Connected to {port}. Logging data to {output_file}.")
    
    with open(output_file, "a") as file:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(line)
                file.write(line + "\n\n")
                file.flush()
except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"\nAn error occurred: {e}")
finally:
    if 'ser' in locals():
        ser.close()
