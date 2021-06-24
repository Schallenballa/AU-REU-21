import os
import time
import board
import busio
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import math
import numpy as np
#from pynput import keyboard                                                      # Import PS-Drone-API
import signal

i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

home_dir = os.path.expanduser('~')
repository_dir = os.path.join(home_dir, 'Desktop/AU-REU-21')


end = False


def shutdown_gracefully(signal, frame):
    exit()

signal.signal(signal.SIGQUIT, shutdown_gracefully)

with open(os.path.join(repository_dir, 'temp.txt'),'w') as file:
    file.write("")
file.close()

with open(os.path.join(repository_dir, 'temp.txt'),'a') as file:
    while not end:
        #print("Accelerometer (m/s^2): X=%0.3f Y=%0.3f Z=%0.3f"%(accel.acceleration[0],accel.acceleration[1],accel.acceleration[2]))
        print("Magnetometer (micro-teslas): X=%4.1f Y=%4.1f Z=%4.1f"%(mag.magnetic[0],mag.magnetic[1],mag.magnetic[2]))
        roll = math.atan2(accel.acceleration[0],accel.acceleration[2])
        #pitch = math.asin(accel.acceleration[0]/9.81)
        angle = math.degrees(math.atan2(mag.magnetic[1],mag.magnetic[0]))
        angle-=80
        if angle<0:
            angle+=360
        acceleration = (math.sqrt(accel.acceleration[0]**2 + accel.acceleration[1]**2 + accel.acceleration[2]**2) - 9.81)
        print("Angle (degrees): "+str(angle))
        print("Acceleration: " + str(acceleration))
        file.write(str(roll)+",")
        #file.write(str(pitch)+"\n")
        time.sleep(.1)
file.close()