FROM python:3
ADD batteryTest.py /
ADD start.sh / -- > Shell script file to run the python file
RUN chmod +x start.sh
RUN pip install pyardrone
