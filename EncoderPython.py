"""
Ejemplo simple que conecta la maquina virtual con el arduino a traves de Python
"""
import time
import serial
import warnings
import numpy as np
from collections import deque
import matplotlib.pyplot as plt


arduino = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=1.0)
arduino.setDTR(False)
time.sleep(1)
arduino.flushInput()
arduino.setDTR(True)


with arduino:
    while True:
        try:
            line = arduino.readline()
            if not line:
            # HACK: Descartamos líneas vacías porque fromstring produce
            # resultados erróneos, ver
            # https://github.com/numpy/numpy/issues/1714
                continue
            line = line.decode('ascii', errors='replace')
            print(line)
            
        except ValueError:
            warnings.warn("Line {} didn't parse, skipping".format(line))
        except KeyboardInterrupt:
            print("Exiting")
            arduino.close()
            break