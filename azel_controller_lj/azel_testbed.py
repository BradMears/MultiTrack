'''Testbed for the az/el controller'''

from time import sleep
import click
from labjack import ljm

MOVE = 1
STOP = 0

def stop_all_motion():
    for pin in [az_right, az_left, el_up, el_down]:
        ljm.eWriteName(handle, pin, STOP)

if __name__ == "__main__":
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    az_right = "FIO7"
    az_left = "FIO6"
    el_up = "FIO5"
    el_down = "FIO4"

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

