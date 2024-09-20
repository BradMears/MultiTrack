'''Testbed for the az/el controller'''

from time import sleep
import board
import digitalio
import click

MOVE = True
STOP = False

def stop_all_motion():
    az_right.value = STOP
    az_left.value = STOP
    el_up.value = STOP
    el_down.value = STOP

if __name__ == "__main__":
    az_right = digitalio.DigitalInOut(board.C3)
    az_right.direction = digitalio.Direction.OUTPUT
    az_right.value = STOP

    az_left = digitalio.DigitalInOut(board.C2)
    az_left.direction = digitalio.Direction.OUTPUT
    az_left.value = STOP

    el_up = digitalio.DigitalInOut(board.C1)
    el_up.direction = digitalio.Direction.OUTPUT
    el_up.value = STOP

    el_down = digitalio.DigitalInOut(board.C0)
    el_down.direction = digitalio.Direction.OUTPUT
    el_down.value = STOP

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
                el_down.value = STOP
                el_up.value = MOVE
            elif c == '\x1b[B':
                click.echo('Decreasing elevation')
                el_up.value = STOP
                el_down.value = MOVE
            elif c == '\x1b[D':
                click.echo('Moving left')
                az_right.value = STOP
                az_left.value = MOVE
            elif c == '\x1b[C':
                click.echo('Moving right')
                az_left.value = STOP
                az_right.value = MOVE
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
