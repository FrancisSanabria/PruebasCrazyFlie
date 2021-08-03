import serial
import matplotlib.pyplot as plt 
from time import sleep
from drawnow import *

arduino = serial.Serial('/dev/ttyACM0')
with arduino:
	arduino.setDTR(False)
	sleep(1)
	arduino.flushInput()
	arduino.setDTR(True)

arduino = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=1.0)
plt.ion ()

count = 0 
AccYarray  = []
AccZarray  = []
tempoarray = []


def fig ():
	plt.plot (AccYarray)
	plt.plot (AccZarray)
	plt.title ('AcelY & AcelZ')
	plt.grid (True)
	plt.plot (AccYarray, 'ro-' , label = 'AcelY')
	plt.plot (AccZarray, 'bo-' , label = 'AcelZ')
	plt.legend (loc= 'upper left')


with arduino:
    while True:
        dadosstring = arduino.readline ()
        AccY = float (dadosstring)
        AccYarray.append (AccY)
        plt.pause (0.00001)
        count = count + 1
        if (count > 50):
        	AccYarray.pop (0)
        tempo = float (dadosstring)
        dadosstring.append (tempo)
        drawnow (fig)