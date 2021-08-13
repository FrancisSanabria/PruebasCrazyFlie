from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


import logging
import cflib
from cflib.crazyflie import Crazyflie
from cflib.utils import uri_helper

#------------------------------------------------------------------------------------------------
#                                  DEFINICION DE CLASES
#------------------------------------------------------------------------------------------------

uri = uri_helper.uri_from_env(default='radio://0/0/250K/E7E7E7E7E7')

logging.basicConfig(level=logging.ERROR)

EstadoConet = False


class MotorRampExample:
    """Example that connects to a Crazyflie and ramps the motors up/down and
    the disconnects"""

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie(rw_cache='./cache')

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        self._cf.open_link(link_uri)

        print('Connecting to %s' % link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Hemos Conecatdo el drone')
        global EstadoConet
        EstadoConet = True

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)

    def _ramp_motors(self):
        thrust_mult = 1
        thrust_step = 500
        thrust = 20000
        pitch = 30
        roll = 0
        yawrate = 0

        # Unlock startup thrust protection
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        while thrust >= 20000:
            self._cf.commander.send_setpoint(roll, 0, yawrate, thrust)
            time.sleep(0.1)
            if thrust >= 25000:
                thrust_mult = -1
            thrust += thrust_step * thrust_mult
        
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        thrust_mult  = 1
        thrust = 20000
        while thrust >= 20000:
            self._cf.commander.send_setpoint(roll, pitch_num, yawrate, thrust)
            time.sleep(0.1)
            if thrust >= 25000:
                thrust_mult = -1
            thrust += thrust_step * thrust_mult
        
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)
        #self._cf.close_link()



#------------------------------------------------------
#                          FUNCIONES
#------------------------------------------------------
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
    global le
    global isRun
    global EstadoConet
    isRun = False
    thread.join()

    if EstadoConet == True:
        le._cf.close_link()
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
plt.title("Lectura de Angulo de Banqueo") #Titulo de la figura # Figure title
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
titulo.grid(row=0,column=0, columnspan=2,pady = 15)


canvas = FigureCanvasTkAgg(fig, master = root)
canvas._tkcanvas.grid(row=1,column=0, rowspan = 3, padx = 15)



def ConectaDrone():
    cflib.crtp.init_drivers()
    global le
    le = MotorRampExample(uri)
    

def DesconectarDrone():
    global EstadoConet
    if (EstadoConet == True):
        global le
        le._cf.close_link()
        print('Desconectando')
        EstadoConet = False
    else:
        print("Operacion no valida")

def RutinaPitch():
    if EstadoConet == True:
        global le
        num = Slider.get()
        global pitch_num
        pitch_num = int(num)
        Thread(target=le._ramp_motors).start()
    else:
        print("El drone no se ha conectado")
    



#----------------------------------- PARA DEFINIR LOS DATOS ENVIADOS -------------------------------
Cuad_ang = LabelFrame(root, text="Angulo Deseado", padx=15 , pady=15)
Cuad_ang.grid(row=1,column=1, padx=30,pady=10) 


Slider = Scale(Cuad_ang, from_= -45, to= 45, orient= HORIZONTAL, length= 200) 
Etiqueta1 = Label(Cuad_ang,text="Angulo de Pitch deseado").grid(row=1,column=1)
Etiqueta2 = Label(Cuad_ang,text="en grados").grid(row=2,column=1) 
Slider.grid(row=3,column=1)
Boton1 = Button(Cuad_ang,text="Iniciar Rutina", command= RutinaPitch).grid(row=4,column=1, pady = 5) #place(x=250,y=150)

ang = StringVar(root, "Angulo Actual: 0.00")
LabelAng = Label(Cuad_ang, textvariable= ang)
LabelAng.grid(row=5,column=1, pady=20)

#----------------------------------- DEFINICION PARA EL PID -------------------------------
Cuad_PID = LabelFrame(root, text="Constantes PID", padx=15 , pady=15)
Cuad_PID.grid(row=2,column=1, padx=30,pady=10) 

KP_L =Label(Cuad_PID,text="Kp  ").grid(row=0,column=0)
KI_L =Label(Cuad_PID,text="Ki  ").grid(row=1,column=0)
KD_L =Label(Cuad_PID,text="Kd  ").grid(row=2,column=0)

KP_E = Entry(Cuad_PID, width=8)
KP_E.grid(row=0,column=1, pady = 3)

KD_E = Entry(Cuad_PID, width=8)
KD_E.grid(row=1,column=1, pady = 3)

KI_E = Entry(Cuad_PID, width=8)
KI_E.grid(row=2,column=1, pady = 3)
Boton_Constantes = Button(Cuad_PID,text="Enviar Constantes").grid(row=4,column=0, columnspan= 2)

#---------------------------------- CONECCION DEL DRONE ---------------------------------------
Cuad_drone = LabelFrame(root, text="Estado del Drone", padx=10 , pady=10)
Cuad_drone.grid(row=3,column=1, padx=30,pady=10) 

Boton_Conect = Button(Cuad_drone,text="Conectar Drone", command= ConectaDrone).grid(row=0,column=0, pady = 3)
Boton_Disconect = Button(Cuad_drone,text="Desconectar Drone", command= DesconectarDrone).grid(row=1,column=0, pady = 3)

anim = animation.FuncAnimation(fig,plotData, fargs=(Samples,lines), interval=sampleTime)


root.mainloop()