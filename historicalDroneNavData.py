import os
import time
import ps_drone
import signal

drone = ps_drone.Drone()                                                      # Start using drone

home_dir = os.path.expanduser('~')
repository_dir = os.path.join(home_dir, 'Desktop/AU-REU-21')

drone.startup()                                                               # Connects to drone and starts subprocesses

drone.reset()                                                                 # Sets drone's status to good (LEDs turn green when red)
while (drone.getBattery()[0] == -1):  time.sleep(0.1)                         # Wait until the drone has done its reset
print ("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1])) # Gives a battery-status
drone.useDemoMode(False)                                                      # Give me everything...fast
drone.getNDpackage(["demo","pressure_raw","altitude","magneto","wifi"])       # Packets, which shall be decoded
time.sleep(1)                                                               # Give it some time to awake fully after reset

##### Mainprogram begin #####
end = False


def shutdown_gracefully(signal, frame):
    exit()

signal.signal(signal.SIGQUIT, shutdown_gracefully)

with open(os.path.join(repository_dir, 'magData.txt'),'w') as file:
    file.write("")
file.close()

with open(os.path.join(repository_dir, 'magData.txt'),'a') as file:
    while not end:
        #print("Magnetometer (micro-Teslas)): X=%i Y=%i Z=%i"%(int(mag.magnetic[0]),int(mag.magnetic[1]),int(mag.magnetic[2])))
        #print("Magnitude (m/s^2): X=%0.3f Y=%0.3f Z=%0.3f"%(accel.acceleration[0],accel.acceleration[1],accel.acceleration[2]))
        print ("Megnetometer [X,Y,Z]:         "+str(drone.NavData["magneto"][0]))
        #file.write("Magnetometer (micro-Teslas)): X=%i Y=%i Z=%i"%(int(mag.magnetic[0]),int(mag.magnetic[1]),int(mag.magnetic[2]))+"\n")
        #file.write("Accelerometer (m/s^2): X=%i Y=%i Z=%i"%(int(accel.acceleration[0]),int(accel.acceleration[1]),int(accel.acceleration[2]))+"\n")
        file.write(str(drone.NavData["magneto"][0][0])+",")
        file.write(str(drone.NavData["magneto"][0][1])+",")
        file.write(str(drone.NavData["magneto"][0][2])+"\n")
        time.sleep(.1)
        #file.write(print1)
        #file.write(print2)
        #maybe store it in an array?
        #or make a function to read in the file as data of an array
file.close()
