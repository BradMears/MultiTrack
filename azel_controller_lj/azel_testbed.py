'''Testbed for the az/el controller using the LabJack device. This script allows you to control the azimuth and elevation.'''

from time import sleep
import click
import GS5500_LabJackIF
from labjack import ljm

# Set pin assignments based on whether we are using the DB15 connector or the main body terminals
USING_DB15 = False  # Set to True if using DB15 connector, False for main body terminals
#USING_DB15 = True # Uncomment this line to use the DB15 connector
INPUT_PORTS, OUPUT_PORTS = GS5500_LabJackIF.use_DB15() if USING_DB15 else GS5500_LabJackIF.use_main_body()

# Define text names we can pass to LJ routines
az_right = OUPUT_PORTS["az_right"]
az_left = OUPUT_PORTS["az_left"]
el_up = OUPUT_PORTS["el_up"]
el_down = OUPUT_PORTS["el_down"]

# Define constants for motion control
MOVE = 1
STOP = 0

def stop_all_motion():
    for pin in [az_right, az_left, el_up, el_down]:
        ljm.eWriteName(handle, pin, STOP)

if __name__ == "__main__":
    # Open the first found LabJack T4. I only have one so conflicts aren't likely.
    # If you have more than one, you may need to specify the serial number or IP
    # address of the LabJack T4 you want to use.
    handle = ljm.openS("T4", "ANY", "ANY")  # Any T4, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    stop_all_motion()

    try:
        click.echo('Press arrow keys to move rotator, q to exit, any other key to stop motion ', nl=False)
        while True:
            c = click.getchar()
            click.echo()
            if c == 'q':
                click.echo('Exiting')
                break
            elif c == '\x1b[A':
                click.echo('Increasing elevation')
                ljm.eWriteName(handle, el_down, STOP)
                ljm.eWriteName(handle, el_up, MOVE)
            elif c == '\x1b[B':
                click.echo('Decreasing elevation')
                ljm.eWriteName(handle, el_up, STOP)
                ljm.eWriteName(handle, el_down, MOVE)
            elif c == '\x1b[D':
                click.echo('Moving left')
                ljm.eWriteName(handle, az_right, STOP)
                ljm.eWriteName(handle, az_left, MOVE)
            elif c == '\x1b[C':
                click.echo('Moving right')
                ljm.eWriteName(handle, az_left, STOP)
                ljm.eWriteName(handle, az_right, MOVE)
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

