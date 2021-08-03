# -*- coding: utf-8 -*-


# Se agregan las librerias necesarias
import logging
import time
from threading import Thread
import cflib
from cflib.crazyflie import Crazyflie
from cflib.utils import uri_helper
import cflib.crtp  # noqa
from cflib.crazyflie.log import LogConfig


uri = uri_helper.uri_from_env(default='radio://0/0/250K/E7E7E7E7E7') #Se establece la banda de conexion
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)



class MotorRampExample:
    """Example that connects to a Crazyflie and ramps the motors up/down and
    the disconnects"""

    def __init__(self, link_uri): # Se define el motor de arranque e inicializacion de variables
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie(rw_cache='./cache')

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        #self.is_connected = True
        

        print('Connecting to %s' % link_uri)

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""

        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=100)
        self._lg_stab.add_variable('stabilizer.roll', 'float')
        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')        


        # Start a separate thread to do the motor test.
        # Do not hijack the calling thread!
        Thread(target=self._ramp_motors).start()

    
    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback from a the log API when data arrives"""
        print(f'[{timestamp}][{logconf.name}]: ', end='')
        for name, value in data.items():
            print(f'{name}: {value:3.3f} ', end='')
        print()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        #self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)
        #self.is_connected = False

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
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
            time.sleep(0.1)
            if thrust >= 25000:
                thrust_mult = -1
            thrust += thrust_step * thrust_mult
        
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        thrust_mult  = 1
        thrust = 20000
        while thrust >= 20000:
            self._cf.commander.send_setpoint(roll, -30, yawrate, thrust)
            time.sleep(0.1)
            if thrust >= 25000:
                thrust_mult = -1
            thrust += thrust_step * thrust_mult
        
        self._cf.commander.send_setpoint(0, 0, 0, 0)

        
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)
        self._cf.close_link()


if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    le = MotorRampExample(uri)

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    '''
    while le.is_connected:
        
        time.sleep(1)
    '''


    

