# Example usage of the LSM303DLHC accelerometer/magnetometer

from time import sleep
import board
import busio
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
from pynput import keyboard

i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

end = False

def on_press(key):
    global end
    end = True
    return False

listener = keyboard.Listener(on_press=on_press)
listener.start()

while not end:
    print("Acceleration (m/s^2): X=%0.3f Y=%0.3f Z=%0.3f"%accel.acceleration)
    print("Magnetometer (micro-Teslas)): X=%0.3f Y=%0.3f Z=%0.3f"%mag.magnetic)
    print("")
    sleep(0.5)
