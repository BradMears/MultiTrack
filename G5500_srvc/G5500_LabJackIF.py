#!/usr/bin/env python3
"""Provide pin assigments for controlling the Yaesu GS5000 through the LabJack T4. 
Yes, this is quite specific to how I wired up my LabJack T4 to my Yaesu GS5000 rotator
but I don't really expect there to be many other people who will have those two pieces
of hardware AND will want to use this software."""

import G5500
from labjack import ljm

# More details on the LabJack T4 can be found here: 
# https://support.labjack.com/docs/4-0-hardware-overview-t-series-datasheet


class G5500_LabJack(G5500.G5500):
    '''Class to control a Yaesu G5500 rotator through a LabJack T4.'''
    
    MOVE = 1
    STOP = 0

    @staticmethod
    def use_db15():
        """Return the db15 pin assignments."""
        INPUT_PORTS = {'az_in': 'AIN8', 
                    'el_in': 'AIN10',
                    'pwr_on_in': 'AIN9'}
        OUPUT_PORTS = {'az_left': 'EIO6', 
                    'az_right': 'EIO4',
                    'el_up': 'CIO3',
                    'el_down': 'CIO1'}
        return INPUT_PORTS, OUPUT_PORTS

    @staticmethod
    def use_main_body():
        """Return the main body pin assignments."""
        INPUT_PORTS = {'az_in': 'AIN0', 
                    'el_in': 'AIN1',
                    'pwr_on_in': 'AIN3'}
        OUPUT_PORTS = {'az_left': 'FIO7', 
                    'az_right': 'FIO6',
                    'el_up': 'FIO5',
                    'el_down': 'FIO4'}
        return INPUT_PORTS, OUPUT_PORTS

    def __init__(self, cal_file : str = 'rotator_cal.txt'):
        '''Constructor. input_ports and output_ports should be dictionaries with the
        names of the LabJack T4 pins to use for each function.'''
        super().__init__(cal_file)
        self.input_ports, self.output_ports = G5500_LabJack.use_main_body()
        self.az_right = self.output_ports["az_right"]
        self.az_left = self.output_ports["az_left"]
        self.el_up = self.output_ports["el_up"]
        self.el_down = self.output_ports["el_down"]
        self.az_in = self.input_ports['az_in']
        self.el_in = self.input_ports['el_in']
        self.pwr_on_in = self.input_ports['pwr_on_in']

        # Open the first found LabJack T4. I only have one so conflicts aren't likely.
        # If you have more than one, you may need to specify the serial number or IP
        # address of the LabJack T4 you want to use.
        self.handle = ljm.openS("T4", "ANY", "ANY")  # Any T4, Any connection, Any identifier
        assert(self.handle is not None), 'LabJack handle is not set. Call open_labjack() first.'
        #info = ljm.getHandleInfo(self.handle)

    def __del__(self):
        """
        The destructor method, called when the object is about to be destroyed.
        """
        try:
            ljm.close(self.handle)
            print(f"LabJack handle closed.")
        except Exception as e:
            print(f"Error closing LabJack handle: {e}") 

    def stop_motion(self):
        '''Stops all motion of the rotator.'''
        ljm.eWriteName(self.handle, self.az_left, G5500_LabJack.STOP)
        ljm.eWriteName(self.handle, self.az_right, G5500_LabJack.STOP)
        ljm.eWriteName(self.handle, self.el_up, G5500_LabJack.STOP)
        ljm.eWriteName(self.handle, self.el_down, G5500_LabJack.STOP)
    
    def move_az_right(self):
        '''Starts motion to increase azimuth.'''
        ljm.eWriteName(self.handle, self.az_left, G5500_LabJack.STOP)
        ljm.eWriteName(self.handle, self.az_right, G5500_LabJack.MOVE)
    
    def move_az_left(self):
        '''Starts motion to decrease azimuth.'''
        ljm.eWriteName(self.handle, self.az_right, G5500_LabJack.STOP)
        ljm.eWriteName(self.handle, self.az_left, G5500_LabJack.MOVE)
    
    def move_el_up(self):
        '''Starts motion to increase elevation.'''
        ljm.eWriteName(self.handle, self.el_down, G5500_LabJack.STOP)
        ljm.eWriteName(self.handle, self.el_up, G5500_LabJack.MOVE)
    
    def move_el_down(self):
        '''Starts motion to decrease elevation.'''
        ljm.eWriteName(self.handle, self.el_up, G5500_LabJack.STOP)
        ljm.eWriteName(self.handle, self.el_down, G5500_LabJack.MOVE)
    
    def read_sensors(self) -> tuple[float, float, bool]:
        '''Reads the current positions from the rotator and updates self.az and self.el.
        Also reads the power-on state of the rotator.
        Returns a tuple of (az, el, pwr_on) in (degrees, degrees, bool).'''
        names = [self.az_in, self.el_in, self.pwr_on_in]
        numFrames = len(names)

        # Setup and call eReadNames to read values from the LabJack.
        az_v, el_v, pwr_on_v = ljm.eReadNames(self.handle, numFrames, names)
        self.az, self.el = self.voltage_to_degrees(az_v, el_v)
        self.pwr_on = pwr_on_v > 2.5  # Assume power is on if voltage is > 2.5V

        return (self.az, self.el, self.pwr_on)

    def __str__(self):
        # Keeping the name short to prevent the print statements from getting too long
        D = u'\N{DEGREE SIGN}'
        az_str = f'{self.az:7.2f}{D}' if self.az is not None else 'None'
        el_str = f'{self.el:7.2f}{D}' if self.el is not None else 'None'
        pwr_str = 'On' if self.pwr_on else 'Off'
        return f'G5500_LabJack(az={az_str}, el={el_str}, pwr_on={pwr_str})'


    

    