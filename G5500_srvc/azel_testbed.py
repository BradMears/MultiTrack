'''Testbed for the az/el controller using the LabJack device. This script allows you to control the azimuth and elevation.'''

from time import sleep
import click
import GS5500
import GS5500_LabJackIF
from labjack import ljm

# Set pin assignments based on whether we are using the DB15 connector or the main body terminals
USING_DB15 = False  # Set to True if using DB15 connector, False for main body terminals
#USING_DB15 = True # Uncomment this line to use the DB15 connector
INPUT_PORTS, OUPUT_PORTS = GS5500_LabJackIF.use_db15() if USING_DB15 else GS5500_LabJackIF.use_main_body()

# Define text names we can pass to LJ routines
az_right = OUPUT_PORTS["az_right"]
az_left = OUPUT_PORTS["az_left"]
el_up = OUPUT_PORTS["el_up"]
el_down = OUPUT_PORTS["el_down"]

# Define constants for motion control
MOVE = 1
STOP = 0

ROTATOR = GS5500.YaesuG5500Positions()  # This will only work if the cal file is up to date

def stop_all_motion():
    '''Stop all motion by writing STOP to all output pins.'''
    for pin in [az_right, az_left, el_up, el_down]:
        ljm.eWriteName(handle, pin, STOP)

def read_inputs():
    '''Read and print the azimuth, elevation, and power status inputs.'''
    names = [INPUT_PORTS['az_in'], INPUT_PORTS['el_in'], INPUT_PORTS['pwr_on_in']]
    numFrames = len(names)
    # Setup and call eReadNames to read values from the LabJack.
    az_v, el_v, pwr_on_v = ljm.eReadNames(handle, numFrames, names)
    print(f'Power signal = {pwr_on_v:7.2f}V\t',end='')
    
    # Axis, MinAngle, MinCount, MinVoltage, MaxAngle, MaxCount, MaxVoltage
    az_deg_v, el_deg_v = ROTATOR.voltage_to_degrees(az_v, el_v)
    az_diff = az_deg_v - az_deg_v
    # Keeping the name short to prevent the print statements from getting too long
    D = u'\N{DEGREE SIGN}'
    print(f'Az = {az_deg_v:7.2f}{D} {az_v:7.2}V\t',end='')
    print(f'El = {el_deg_v:7.2f}{D} {el_v:7.2}V')


if __name__ == "__main__":
    # Open the first found LabJack T4. I only have one so conflicts aren't likely.
    # If you have more than one, you may need to specify the serial number or IP
    # address of the LabJack T4 you want to use.
    handle = ljm.openS("T4", "ANY", "ANY")  # Any T4, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    stop_all_motion()

    try:
        click.echo('Press arrow keys to move rotator, q to exit, any other key to stop motion ', nl=False)
        while True:
            c = click.getchar()
            #print(f'Got character: {repr(c)}')
            click.echo()
            # The escape sequences for arrow keys are a bit different between normal mode
            # and application mode. I haven't figured out how to force one or the other.
            # So we just check for both.
            if c == 'q':
                click.echo('Exiting')
                break
            elif c == '\x1b[A' or c == '\x1bOA':
                click.echo('Increasing elevation')
                ljm.eWriteName(handle, el_down, STOP)
                ljm.eWriteName(handle, el_up, MOVE)
            elif c == '\x1b[B' or c == '\x1bOB':
                click.echo('Decreasing elevation')
                ljm.eWriteName(handle, el_up, STOP)
                ljm.eWriteName(handle, el_down, MOVE)
            elif c == '\x1b[C' or c == '\x1bOC':
                click.echo('Moving right')
                ljm.eWriteName(handle, az_left, STOP)
                ljm.eWriteName(handle, az_right, MOVE)
            elif c == '\x1b[D' or c == '\x1bOD':
                click.echo('Moving left')
                ljm.eWriteName(handle, az_right, STOP)
                ljm.eWriteName(handle, az_left, MOVE)
            elif c == 'r':
                click.echo('Reading inputs')
                read_inputs()
            elif c == 'e':
                raise ValueError("Deliberate exception")
            else:
                stop_all_motion()
                click.echo('Stopping motion')

    except Exception as e:
        stop_all_motion()
        print('Caught exception and turned everything off')
        print(e)

    stop_all_motion()
    # Close handle
    ljm.close(handle)

