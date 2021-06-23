import matplotlib.pyplot as plt
import os

home_dir = os.path.expanduser('~')
repository_dir = os.path.join(home_dir, 'Desktop/AU-REU-21')

x1 = []

x2 = []

x3 = []

y1 = []

yCounter = 0

with open(os.path.join(repository_dir, 'temp.txt'),'r') as file:
    line=file.readline()
    for line in file:
        xTemp = line.split(',')
        x1.append(int(xTemp[0]))
        x2.append(int(xTemp[1]))
        x3.append(int(xTemp[2]))
        y1.append(yCounter)
        yCounter += 1

plt.plot(y1,x1, color='red',label = "X - Magnitude")

plt.plot(y1,x2, color='green',label = "Y - Magnitude")

plt.plot(y1,x3, color='blue',label = "Z - Magnitude")

plt.xlabel('1/10th seconds')

plt.ylabel('Magnitude (micro-teslas)')

plt.title('Timeline of Magnitude')

plt.show()