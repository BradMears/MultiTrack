#!/usr/bin/env python3
"""Provide pin assigments for controlling the Yaesu GS5000 through the LabJack T4. 
Yes, this is quite specific to how I wired up my LabJack T4 to my Yaesu GS5000 rotator
but I don't really expect there to be many other people who will have those two pieces
of hardware AND will want to use this software."""

# More details on the LabJack T4 can be found here: 
# https://support.labjack.com/docs/4-0-hardware-overview-t-series-datasheet

# Top row of the LabJack T4 db15 connector (left to right):
# GND
# EIO6 = DIO14
# EIO4 = DIO12
# EIO2 = DIO10 = AIN10
# EIO0 = DIO8 = AIN8
# CIO3 = DIO19
# CIO1 = DIO17
# VS 

# Bottom row of the LabJack T4 db15 connector (left to right):
# EIO7 = DIO15
# EIO5 = DIO13
# EIO3 = DIO11
# EIO1 = DIO9
# GND
# CIO2 = DIO18
# CIO0 = DIO16

class LabJackT4db15ToYaesuGS5500:
    # This configuration uses seven of the eight pins on the top row
    # GND, 4 outputs, and 2 inputs
    INPUT_PORTS = {'az_in': 'AIN8', 
                   'el_in': 'AIN10'}
    OUPUT_PORTS = {'az_left': 'EIO6', 
                   'az_right': 'EI04',
                   'el_up': 'CIO3',
                   'el_down': 'CIO1'}

class LabJackT4MainBodyToYaesuGS5500:
    INPUT_PORTS = {'az_in': 'AIN0', 
                   'el_in': 'AIN1'}
    OUPUT_PORTS = {'az_left': 'FIO6', 
                   'az_right': 'FIO7',
                   'el_up': 'FIO5',
                   'el_down': 'FIO4'}

def use_db15():
    """Return the db15 pin assignments."""
    return LabJackT4db15ToYaesuGS5500.INPUT_PORTS, LabJackT4db15ToYaesuGS5500.OUPUT_PORTS

def use_main_body():
    """Return the main body pin assignments."""
    return LabJackT4MainBodyToYaesuGS5500.INPUT_PORTS, LabJackT4MainBodyToYaesuGS5500.OUPUT_PORTS
