from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


isReceiving = False # bandera para comenzar a recibir datos / flag for start receive data 
isRun = True # bandera para recibir datos /  flag for receive data 
value = 0.0 #  dato de sensor / data sensor

def getData(): 
        time.sleep(1.0)  # dar tiempo para comenzar a recibir datos / give some time for retrieving data
        serialConnection.reset_input_buffer() #  resetear el buffer de entrada / reset input buffer 

        while (isRun):  # leer datos / retrieve data 
            global isReceiving
            global value
            value  = float(serialConnection.readline().strip())  #Leer sensor / Read sensor
            value =  np.degrees(np.arctan2(np.sin(np.radians(value)),np.cos(np.radians(value))))
            isReceiving = True 

def askQuit():
    global isRun
    isRun = False
    thread.join()
    serialConnection.close()
    root.quit()
    root.destroy()

def plotData(self,Samples, lines):
    global value
    data.append(value) #Guarda lectura en la última posición / #Save reading in the end position
    lines.set_data(range(Samples),data) # Dibujar nueva linea / Drawn new line
    ang.set("Angulo Actual: "+str(round(value,2)))
    #lineValueText.set_text(lineLabel+' = ' + str(round(value,2))) # Mostrar valor del sensor / Show sensor value


#-----------------------------VARIABLES-------------------------------------
serialPort = '/dev/ttyACM0' # Puerto serial arduino / Arduino serial port
baudRate = 115200  # Baudios
isReceiving = False
isRun = True
value = 0.0

try:
  serialConnection = serial.Serial(serialPort, baudRate) # Instanciar objeto Serial / Instance Serial Object
except:
  print('No se puede conectar al puerto')


thread = Thread(target=getData) # Crear objeto de la clase Thread 
thread.start() #Iniciar subproceso / Star subprocess

while isReceiving != True: # Esperar hasta recibir datos
    print("Starting receive data")
    time.sleep(0.1)

  

Samples = 100  #Muestras / Samples
data = collections.deque([0] * Samples, maxlen=Samples) # Vector de muestras/ Sample Vector
sampleTime = 60  #Tiempo de muestreo / Sample Time

# Limites de los ejes / Axis limit
xmin = 0
xmax = Samples
ymin = -180
ymax = 180

fig = plt.figure(facecolor='0.94')# Crea una nueva figura #Create a new figure.
ax  = plt.axes(xlim=(xmin, xmax), ylim=(ymin , ymax))
plt.title("Real-time Sensor reading") #Titulo de la figura # Figure title
ax.set_xlabel("Muestras")
ax.set_ylabel("Anulo en grados")
lines = ax.plot([], [])[0]

"""
lineLabel = 'Pitch Angle'
lines = ax.plot([], [], label=lineLabel)[0] # Grafica datos iniciales y retorna lineas que representan la gráfica/ Plot initial data and Return a list of Line2D objects representing the plotted data.
lineValueText = ax.text(0.85, 0.95, '', transform=ax.transAxes) #Agregue texto en la ubicación x , y (0 a 1) / Add text at location x, y (0 to 1)
"""
# ------------------------- DEFINICION DE TK INTER ---------------------------------
root = Tk()
root.protocol('WM_DELETE_WINDOW', askQuit)
root.title("Control de orientación - Crazyflie")
titulo = Label(root, text="VENTANA PRINCIPAL", font = ("Helvetica",15,"bold"))
titulo.grid(row=0,column=0, columnspan=2)


canvas = FigureCanvasTkAgg(fig, master = root)
canvas._tkcanvas.grid(row=1,column=0)


def EnviarComandos():
    num = Slider.get()
    global pitch_num
    pitch_num = int(num)
    #cflib.crtp.init_drivers()
    #le = MotorRampExample(uri)


#----------------------------------- PARA DEFINIR LOS DATOS ENVIADOS -------------------------------
Cuad_ang = LabelFrame(root, text="Angulo Deseado", padx=15 , pady=15)
Cuad_ang.grid(row=1,column=1, padx=30) 

#e_pitch = Entry(Cuad_ang)
#e_pitch.grid(row=1,column=1)

Slider = Scale(Cuad_ang, from_= -45, to= 45, orient= HORIZONTAL, length= 200) 
Etiqueta1 = Label(Cuad_ang,text="Angulo de Pitch deseado").grid(row=1,column=1)
Etiqueta2 = Label(Cuad_ang,text="en grados").grid(row=2,column=1) 
Slider.grid(row=3,column=1)
Boton1 = Button(Cuad_ang,text="Iniciar Rutina", command= EnviarComandos).grid(row=4,column=1) #place(x=250,y=150)

ang = StringVar(root, "Angulo Actual: 0.00")
LabelAng = Label(Cuad_ang, textvariable= ang)
LabelAng.grid(row=5,column=1, pady=20)


    
anim = animation.FuncAnimation(fig,plotData, fargs=(Samples,lines), interval=sampleTime)

root.mainloop()