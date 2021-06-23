import os
import time
import board
import busio
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
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
        #print("Magnetometer (micro-Teslas)): X=%i Y=%i Z=%i"%(int(mag.magnetic[0]),int(mag.magnetic[1]),int(mag.magnetic[2])))
        print("Magnetometer (micro-teslas): X=%0.3f Y=%0.3f Z=%0.3f"%(mag.magnetic[0],mag.magnetic[1],mag.magnetic[2]))
        #file.write("Magnetometer (micro-Teslas)): X=%i Y=%i Z=%i"%(int(mag.magnetic[0]),int(mag.magnetic[1]),int(mag.magnetic[2]))+"\n")
        #file.write("Accelerometer (m/s^2): X=%i Y=%i Z=%i"%(int(accel.acceleration[0]),int(accel.acceleration[1]),int(accel.acceleration[2]))+"\n")
        file.write(str(int(mag.magnetic[0]))+",")
        file.write(str(int(mag.magnetic[1]))+",")
        file.write(str(int(mag.magnetic[2]))+"\n")
        time.sleep(.1)
        #file.write(print1)
        #file.write(print2)
        #maybe store it in an array?
        #or make a function to read in the file as data of an array
file.close()
