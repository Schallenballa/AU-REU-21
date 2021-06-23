#THIS PROGRAM WILL RETURN A VALUE DETECTING IF IT HAS DRIFTED TO THE RIGHT OR THE LEFT
#It does this by adding all of the y-axis values and detecting if they are net-positive or net-negative

import os
import time
import board
import busio
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import matplotlib.pyplot as plt
import signal

i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

home_dir = os.path.expanduser('~')
repository_dir = os.path.join(home_dir, 'Desktop/AU-REU-21')


end = False


x1 = []

x2 = []

x3 = []

y1 = []

yCounter = 0

def determineResult():
    global x2
    netTotal = 0
    print("Calculating result...")
    time.sleep(3)
    for value in x2:
        netTotal += value
    if (netTotal > 0):
        print("The y-axis is net-positive")
    elif (netTotal == 0):
        print("The y-axis is net-zero")
    else:
        print("The y-axis is net-negative")
    print("netTotal: "+netTotal)

def shutdown_gracefully(signal, frame):
    determineResult()

signal.signal(signal.SIGQUIT, shutdown_gracefully)

with open(os.path.join(repository_dir, 'temp.txt'),'w') as file:
    file.write("")
file.close()

with open(os.path.join(repository_dir, 'temp.txt'),'a') as file:
    print("Gathering data...")
    time.sleep(.5)
    print("Press CTRL + \ to finish gathering data")
    while not end:
        #print("Magnetometer (micro-Teslas)): X=%i Y=%i Z=%i"%(int(mag.magnetic[0]),int(mag.magnetic[1]),int(mag.magnetic[2])))
        #print("Accelerometer (m/s^2): X=%0.3f Y=%0.3f Z=%0.3f"%(accel.acceleration[0],accel.acceleration[1],accel.acceleration[2]))
        #file.write("Magnetometer (micro-Teslas)): X=%i Y=%i Z=%i"%(int(mag.magnetic[0]),int(mag.magnetic[1]),int(mag.magnetic[2]))+"\n")
        #file.write("Accelerometer (m/s^2): X=%i Y=%i Z=%i"%(int(accel.acceleration[0]),int(accel.acceleration[1]),int(accel.acceleration[2]))+"\n")
        file.write(str(int(accel.acceleration[0]))+",")
        file.write(str(int(accel.acceleration[1]))+",")
        file.write(str(int(accel.acceleration[2]))+"\n")
        time.sleep(.1)
        #file.write(print1)
        #file.write(print2)
        #maybe store it in an array?
        #or make a function to read in the file as data of an array


with open(os.path.join(repository_dir, 'temp.txt'),'r') as file:
    line=file.readline()
    for line in file:
        xTemp = line.split(',')
        x1.append(int(xTemp[0]))
        x2.append(int(xTemp[1]))
        x3.append(int(xTemp[2]))
        y1.append(yCounter)
        yCounter += 1


file.close()
