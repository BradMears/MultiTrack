#!/usr/bin/env python3
"""Service to control the Yaesu GS5500 rotator. Accepts commands over a TCP socket.
Can utilize either the LabJack T4 or the FT232H as the interface to the Rotator 
Interface Circuit (RIC). The RIC is the completely pretentious name for the very 
simple circuit that connects the rotator to the computer. It consist of not much 
more than four transistors to switch the motor drive lines and a voltage divider."""

import argparse
import logging
import socket
import sys
import argparse_config_file
from G5500 import G5500

CONFIG_FILE='G5500_config.txt'

# Port number was selected by browing for unused ones on https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
DEFAULT_PORT=9040 # Default port for the service to listen on

# Define the set of command-line arguments
parser = argparse_config_file.ArgumentParserWithConfig(description=__doc__)
parser.add_argument('--conf_export', action='store_true')
parser.add_argument('--elevation_m', type=float, default=0)
parser.add_argument('--longitude', type=float, default=0)
parser.add_argument('--latitude', type=float, default=0)
parser.add_argument('--interactive', action='store_true')
parser.add_argument('--port', type=int, default=DEFAULT_PORT)
parser.add_argument(
    "--hw_interface",
    choices=["LabJack", "FT232H"],
    default="LabJack",
    help="Choose one of the allowed interfaces."
)

def sanity_test_config(args):
    '''Check that the configuration parameters are reasonable.'''
    if args.longitude < -180 or args.longitude > 180:
        print(f'Longitude {args.longitude} is out of range')
        sys.exit(1)
    if args.latitude < -90 or args.latitude > 90:
        print(f'Latitude {args.latitude} is out of range')
        sys.exit(1)
    if args.elevation_m < -430 or args.elevation_m > 8850: # Dead Sea shore to Mt Everest
        print(f'Elevation {args.elevation_m} is out of range')
        sys.exit(1)
    if args.port < 1024 or args.port > 65535:
        print(f'Port {args.port} is out of range. Must be between 1024 and 65535')
        sys.exit(1)

def interactive_mode( g5500 : G5500 ):
    '''Run the interactive mode. The user can control the rotator with the keyboard.'''
    import click

    g5500.stop_motion()

    try:
        click.echo('Press arrow keys to move rotator, q to exit, any other key to stop motion ', nl=False)
        while True:
            c = click.getchar()
            #print(f'Got character: {repr(c)}')
            click.echo()
            # The escape sequences for arrow keys are a bit different between normal mode
            # and application mode. I haven't figured out how to force one or the other,
            # so we just check for both.
            if c == 'q':
                #click.echo('Exiting')
                break
            elif c == '\x1b[A' or c == '\x1bOA':
                click.echo('Increasing elevation')
                g5500.move_el_up()
            elif c == '\x1b[B' or c == '\x1bOB':
                click.echo('Decreasing elevation')
                g5500.move_el_down()
            elif c == '\x1b[C' or c == '\x1bOC':
                click.echo('Moving right')
                g5500.move_az_right()
            elif c == '\x1b[D' or c == '\x1bOD':
                click.echo('Moving left')
                g5500.move_az_left()
            elif c == 'r':
                click.echo('Reading inputs')
                g5500.read_sensors()
                print(g5500)
            elif c == 'e':
                raise ValueError("Deliberate exception")
            else:
                g5500.stop_motion()
                click.echo('Stopping motion')

    except Exception as e:
        g5500.stop_motion()
        print('Caught exception and turned everything off')
        print(e)

    g5500.stop_motion()

    print('Exiting interactive mode')

if __name__ == "__main__":
    # Load configuration file and apply command-line overrides
    try:
        args = parser.load_args_and_overrides(CONFIG_FILE)
    except FileNotFoundError as e:
        print(e)
        print('Using defaults and command-line only')
        args = parser.parse_args()

    sanity_test_config(args)
    if args.conf_export:
        print(f'Exporting configuration to {CONFIG_FILE}')
        parser.export_config(CONFIG_FILE, args)
        sys.exit(0)

    print(f'{args.hw_interface=}')
    if args.hw_interface == 'LabJack':
        import G5500_LabJackIF as G5500_IF
        g5500 = G5500_IF.G5500_LabJack()
    else:
        #import G5500_FT232HIF as G5500_IF
        g5500 = None
        raise NotImplementedError('FT232H interface not implemented yet')

    if args.interactive:
        print("Using interactive mode")
        interactive_mode(g5500)
    else:
        print("Using service mode")
        print('Exiting service mode - not implemented yet')
