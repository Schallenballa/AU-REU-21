import matplotlib.pyplot as plt
import os

home_dir = os.path.expanduser('~')
repository_dir = os.path.join(home_dir, 'Desktop/AU-REU-21')

x1 = []

x2 = []

y1 = []

yCounter = 0

with open(os.path.join(repository_dir, 'temp.txt'),'r') as file:
    line=file.readline()
    for line in file:
        xTemp = line.split(',')
        xTemp2 = xTemp[1].split('\n')
        x1.append(float(xTemp[0]))
        x2.append(float(xTemp2[0]))
        y1.append(yCounter)
        yCounter += 1

plt.plot(y1,x1, color='red',label = "Pitch (radians)")

plt.plot(y1,x2, color='green',label = "Roll (radians)")

plt.xlabel('1/10th seconds')

plt.ylabel('Radians')

plt.title('Timeline of Pitch/Roll')

plt.show()