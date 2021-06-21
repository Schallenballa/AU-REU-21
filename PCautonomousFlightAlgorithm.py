#Pseudocode to try
#This is a simulated program
import time
import os
import board
import busio
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag


os.system('clear')
i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
#Pseduocode for alignmentAlgorithm()
def alignmentAlgorithm():
    print("Running alignment algorithm!")

#Function to convert time object to printable statement
def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60

  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),int(sec)))

detectAprilTag = False
poseThreshold = 10000000
start_time = time.time()
timeAllotted = start_time + 20
while (timeAllotted > time.time()):
    #print("Drone is moving forward...")
    current_time = int(time.time())
    if (detectAprilTag == True):
        print("AprilTag is detected!")
        print("Running the alignmentAlgorithm()...")
        break
    else:
        if (poseThreshold < 0):
            os.system('clear')
            print("Pose threshold is now negative")
            alignmentAlgorithm()
            break
        if (current_time == int(time.time())):
            continue
        else:
            os.system('clear')
            time_convert(time.time())
            print("Magnetometer (micro-Teslas)): X=%0.3f Y=%0.3f Z=%0.3f"%mag.magnetic)
print("While loop has concluded")
finish = time.time()
time_convert(finish - start_time)
