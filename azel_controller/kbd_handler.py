'''Example code for using the click library to read the arrow keys on the keyboard. Comments
are written as if this script were controlling antenna motion, which it isn't.'''
import click

try:
    click.echo('Press arrow keys to move rotator, q to exit, any other key to stop motion ', nl=False)
    while True:
        c = click.getchar()
        click.echo()
        if c == 'q':
            click.echo('Exiting')
            break
        elif c == '\x1b[A':
            # Turn off down
            # Turn on Up
            click.echo('Increasing elevation')
        elif c == '\x1b[B':
            # Turn off up
            # Turn on down
            click.echo('Decreasing elevation')
        elif c == '\x1b[D':
            # Turn off right
            # Turn on left
            click.echo('Moving left')
        elif c == '\x1b[C':
            # Turn off left
            # Turn on right
            click.echo('Moving right')
        elif c == 'e':
            raise ValueError("Deliberate exception")
        else:
            #  Turn off all motion
            click.echo('Stopping motion')

except Exception as e:
    #  Turn off all motion
    print('Caught exception and turned everything off')
    print(e)

#  Turn off all motion
