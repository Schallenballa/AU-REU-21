import matplotlib.pyplot as plt
import os

home_dir = os.path.expanduser('~')
repository_dir = os.path.join(home_dir, 'Desktop/AU-REU-21')

x1 = []

y1 = []

yCounter = 0

with open(os.path.join(repository_dir, 'yawData.txt'),'r') as file:
    line=file.readline()
    for line in file:
        x1.append(line)
        y1.append(yCounter)
        yCounter += 1

plt.plot(y1,x1, color='blue',label = "Yaw/Heading")

plt.xlabel('1/10th seconds')

plt.ylabel('Degrees')

plt.title('Timeline of Yaw/Heading')

plt.show()
