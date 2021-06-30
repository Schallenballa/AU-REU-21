# Example usage of the LSM303DLHC accelerometer/magnetometer

import board
import busio
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
#from pynput import keyboard
import signal
import math
from time import sleep

i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

end = False

# def on_press(key):
#     global end
#     end = True
#     return False
# 
# listener = keyboard.Listener(on_press=on_press)
# listener.start()

def exit_gracefully(signal, frame):
    print("Ending")
    global end
    end = True

signal.signal(signal.SIGQUIT, exit_gracefully)

while not end:
    print("Acceleration (m/s^2): X=%0.3f Y=%0.3f Z=%0.3f"%accel.acceleration)
    print("Magnetometer (micro-Teslas)): X=%0.3f Y=%0.3f Z=%0.3f"%mag.magnetic)
    angle = math.degrees(math.atan2(mag.magnetic[1],mag.magnetic[0]))
    angle-=80
    if angle<0:
        angle+=360
    print("Angle (degrees): "+str(angle))
    print("")
    sleep(0.5)
    
print("Done")
