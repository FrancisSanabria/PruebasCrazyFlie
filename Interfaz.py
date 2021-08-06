# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
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
"""
Simple example that connects to the first Crazyflie found, ramps up/down
the motors and disconnects.
"""





#------------------------------------------------------------------------------------------------
#                                   IMPORTE DE LIBRERIAS
#------------------------------------------------------------------------------------------------
from tkinter import * 

import logging
import time
from threading import Thread

import cflib
from cflib.crazyflie import Crazyflie
from cflib.utils import uri_helper



#------------------------------------------------------------------------------------------------
#                                  DEFINICION DE CLASES
#------------------------------------------------------------------------------------------------

uri = uri_helper.uri_from_env(default='radio://0/0/250K/E7E7E7E7E7')

logging.basicConfig(level=logging.ERROR)


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

        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        Thread(target=self._ramp_motors).start()

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
        self._cf.close_link()


#------------------------------------------------------------------------------------------------
#                                  CREACION DE INTEFAZ
#------------------------------------------------------------------------------------------------


    



ventana = Tk()
ventana.title("Controlando al Crazyflie")
#ventana.geometry("400x200")
ventana.resizable(0,0)

titulo = Label(ventana, text="Mandar comandos de angulo al Crazyflie", font = ("Helvetica",15,"bold"))
titulo.grid(row=0,column=0,columnspan=3)

e_pitch = Entry(ventana)

e_pitch.grid(row=1,column=1) 

def EnviarComandos():
    num = e_pitch.get()
    global pitch_num
    pitch_num = int(num)
    cflib.crtp.init_drivers()
    le = MotorRampExample(uri)

Boton1 = Button(ventana,text="EnviarCrazyflie", command= EnviarComandos).grid(row=2,column=1) #place(x=250,y=150)
Etiqueta1 = Label(ventana,text="Angulo de Pitch").grid(row=1,column=0)
Etiqueta2 = Label(ventana,text="grados").grid(row=1,column=2) 

ventana.mainloop()