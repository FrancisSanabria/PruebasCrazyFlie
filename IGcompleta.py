# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___//media/sf_VM_SHARE_TESIS/ResultadoPruebas/
#
#  Copyright (C) 2014 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
#
#  Modificaciones realizadas por Francis Sanabria, como proyecto de
#  graduacion para obtener el titulo de Ingeniero Mecatronico

"""
Este documento presenta el codigo que sera utilizado para
"""
from threading import Thread
from numpy.lib.function_base import append
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
import pandas as pd


import logging
import cflib
from cflib.crazyflie import Crazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig


#---------------------------------
# FUNCION PARA CREAR UN CIRCULO
#---------------------------------


#------------------------------------------------------------------------------------------------
#                                  DEFINICION DE CLASES
#------------------------------------------------------------------------------------------------

uri = uri_helper.uri_from_env(default='radio://0/0/250K/E7E7E7E7E7')

logging.basicConfig(level=logging.ERROR)

root = Tk()

EstadoConet = False
textConet = StringVar()
textConet.set("El dron se encuentra DESCONECTADO")




class MotorRampExample:
    """Example that connects to a Crazyflie and ramps the motors up/down and
    the disconnects"""
#
#  Modificaciones realizadas por Francis Sanabria, como proyecto de
#  graduacion para obtener el titulo de Ingeniero Mecatronico
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

        #Codigo agregado para el sistema

        #"""
        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=100)

        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('pid_Constant.pitch_kp_c', 'float')
        self._lg_stab.add_variable('pid_Constant.pitch_ki_c', 'float')
        self._lg_stab.add_variable('pid_Constant.pitch_kd_c', 'float')
       

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            #self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')
        # """

        print('Successful connection')
        global EstadoConet
        EstadoConet = True
        textConet.set("El dron se encuentra CONECTADO")
        
    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback from a the log API when data arrives"""
        #print(f'[{timestamp}][{logconf.name}]: ', end='')
        for name, value in data.items():
            print(f'{name}: {value:3.3f} ', end='')
        print()

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
        pitch = 0
        roll = 0
        yawrate = 0

        global GrafFinal
        global DatoFinal
        DatoFinal = []
        GrafFinal = True

        self._cf.commander.send_setpoint(0, 0, 0, 0)
        for i in range(300):
            self._cf.commander.send_setpoint(roll, pitch_num, yawrate, thrust)
            time.sleep(0.01)
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)
        GrafFinal = False



#------------------------------------------------------
#                          FUNCIONES
#------------------------------------------------------
isReceiving = False # bandera para comenzar a recibir datos / flag for start receive data 
isRun = True # bandera para recibir datos /  flag for receive data 
value = 0.0 #  dato de sensor / data sensor

# ----------- pra plotear data de la ultima grafica --------------
GrafFinal = False
DatoFinal = []




def getData(): 
        time.sleep(1.0)  # dar tiempo para comenzar a recibir datos / give some time for retrieving data
        serialConnection.reset_input_buffer() #  resetear el buffer de entrada / reset input buffer 

        while (isRun):  # leer datos / retrieve data 
            global isReceiving
            global value
            serialConnection.write(b'Z')
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

    # ---- Toma los datos para graficar la nueva figura--------------
    global DatoFinal
    global line2
    if (GrafFinal == True):
        DatoFinal.append(value) #Lectura de datos donde grafica la nueva figura
        #plt.plot(DatoFinal)

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

  

Samples = 150  #Muestras / Samples
data = collections.deque([0] * Samples, maxlen=Samples) # Vector de muestras/ Sample Vector
sampleTime = 20  #Tiempo de muestreo / Sample Time

# Limites de los ejes / Axis limit
xmin = 0
xmax = Samples
ymin = -180
ymax = 180


# ---------------------- Figura Principal Interactiva ------------------------
fig = plt.figure(facecolor='0.94')# Crea una nueva figura #Create a new figure.
ax  = plt.axes(xlim=(xmin, xmax), ylim=(ymin , ymax))
plt.title("Lectura de Angulo de Banqueo") #Titulo de la figura # Figure title
ax.set_xlabel("Muestras")
ax.set_ylabel("Angulo en grados")
lines = ax.plot([], [], label = 'Pitch Angle', color = 'red')[0]

"""
#---------------- Figura 2
fig2 = plt.figure(facecolor='0.94')# Crea una nueva figura #Create a new figure.
ax2  = plt.axes(xlim=(xmin, xmax), ylim=(ymin , ymax))
plt.title("Muestreo de Corrida") #Titulo de la figura # Figure title
ax2.set_xlabel("Muestras")
ax2.set_ylabel("Angulo en grados")
#line2 = ax2.plot([], [], label = 'Pitch Angle Muestra', color = 'blue')[0]
"""
# ------------------------- DEFINICION DE TK INTER ---------------------------------

root.protocol('WM_DELETE_WINDOW', askQuit)
root.title("Control de orientación - Crazyflie")
titulo = Label(root, text="VENTANA PRINCIPAL", font = ("Helvetica",15,"bold"))
titulo.grid(row=0,column=0, columnspan=2,pady = 15)


# Se incluye la grafica en la interfaz
canvas = FigureCanvasTkAgg(fig, master = root)
canvas._tkcanvas.grid(row=1,column=0, rowspan = 3, padx = 15)

#canvas2 = FigureCanvasTkAgg(fig2, master = root)
#canvas2._tkcanvas.grid(row=1,column=4, rowspan = 3, padx = 15)


def ConectaDrone():
    if (EstadoConet == True):
        messagebox.showwarning('Operacion no valida', 'El Crazyflie ya se encunetra conectado')
    else:   
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
        textConet.set("El dron se encuentra DESCONECTADO")
        
    else:
        messagebox.showwarning('Operacion no valida', 'El Crazyflie ya se encunetra desconectado')

def RutinaPitch():
    if EstadoConet == True:
        global le
        num = Slider.get()
        global pitch_num
        pitch_num = int(num)

        #plt.axhline(pitch_num, color = 'b', lw = 1, linestyle = '--')
        Thread(target=le._ramp_motors).start()
        
    else:
        messagebox.showerror('Error de Conexion','No se ha conectado el Crazyflie')




def TararEncoder():
    global serialConnection
    serialConnection.write(b'T')

def EnviarConstantes():  #Las constantes iniciales son Kp = 6.0- Ki = 3.0  - Kd = 0.0
    if EstadoConet == True:
        global le
        c_kp = float(KP_E.get())
        c_ki = float(KI_E.get())
        c_kd = float(KD_E.get())
        le._cf.param.set_value('pid_Constant.pitch_kp_c',c_kp)
        le._cf.param.set_value('pid_Constant.pitch_ki_c',c_ki)
        le._cf.param.set_value('pid_Constant.pitch_kd_c',c_kd)
        KP_E.delete(0,END)
        KI_E.delete(0,END)
        KD_E.delete(0,END)        
        print('Controller setting completed')
    else:
        messagebox.showerror('Error de Conexion','No se ha conectado el Crazyflie')

def ReseteandoConstantes():  #Las constantes iniciales son Kp = 6.0- Ki = 3.0  - Kd = 0.0
    if EstadoConet == True:
        global le
        le._cf.param.set_value('pid_Constant.pitch_kp_c',float(6.0))
        le._cf.param.set_value('pid_Constant.pitch_ki_c',float(3.0))
        le._cf.param.set_value('pid_Constant.pitch_kd_c',float(0.0))
        print('Resetting completed')
    else:
        messagebox.showerror('Error de Conexion','No se ha conectado el Crazyflie')

    
def GuardarCorrida():
    if EstadoConet == True:
        global DatoFinal
        global pitch_num
        plt.figure(2)
        plt.clf()
        plt.subplot(111)
        plt.plot(DatoFinal)
        plt.axhline(pitch_num, color = 'b', lw = 1, linestyle = '--') 
        plt.title("Grafico de Corrida") #Titulo de la figura # Figure title
        plt.xlabel('Muestras')
        plt.ylabel('Angulo de Banqueo')
        plt.savefig('/media/sf_VM_SHARE_TESIS/ResultadoPruebas/Prueba.png')
        #exportar data de python a csv
        df_Pitch = pd.DataFrame(DatoFinal)
        df_Pitch.to_csv('/media/sf_VM_SHARE_TESIS/ResultadoPruebas/DataPitch.csv')
    else:
        messagebox.showerror('Error de Conexion','No se ha conectado el Crazyflie')
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
KP_E.insert(0,"6.0")

KI_E = Entry(Cuad_PID, width=8)
KI_E.grid(row=1,column=1, pady = 3)
KI_E.insert(0,"3.0")

KD_E = Entry(Cuad_PID, width=8)
KD_E.grid(row=2,column=1, pady = 3)
KD_E.insert(0,"0.0")

Boton_Constantes = Button(Cuad_PID,text="Enviar Constantes", command= EnviarConstantes).grid(row=4,column=0, columnspan= 2)
Reset_Constantes = Button(Cuad_PID,text="Reset Constantes", command= ReseteandoConstantes).grid(row=5,column=0, columnspan= 2)
Boton_Show = Button(Cuad_PID,text="Guardar Corrida", command= GuardarCorrida).grid(row=6,column=0, columnspan= 2)

#---------------------------------- CONECCION DEL DRONE ---------------------------------------
Cuad_drone = LabelFrame(root, text="Estado del Drone", padx=10 , pady=10)
Cuad_drone.grid(row=4,column=0, padx=30,pady=10) 

Boton_Conect = Button(Cuad_drone,text="Conectar Drone", command= ConectaDrone).grid(row=0,column=0, pady = 3)
Boton_Disconect = Button(Cuad_drone,text="Desconectar Drone", command= DesconectarDrone).grid(row=1,column=0, pady = 3)
Boton_Tarar = Button(Cuad_drone,text="Tarar", command= TararEncoder).grid(row=3,column=0, pady = 3)
# INDICACION DE ESTADO DE CONEXION
DescConexion = Label(Cuad_drone, textvariable= textConet).grid(row=4,column=0,pady = 4)

anim = animation.FuncAnimation(fig,plotData, fargs=(Samples,lines), interval=sampleTime) #Animacion de la figura




root.mainloop()

