#!/usr/bin/env python3
'''Testbed application for developing a way to process command-line arguments
that can also be specified in a config file.'''

import argparse_config_file
import json

CONFIG_FILE='observer.txt'

# Define the set of command-line arguments
parser = argparse_config_file.ArgumentParserWithConfig(description=__doc__)
parser.add_argument('--conf_export', action='store_true')
parser.add_argument('--elevation_m', type=float, default=0)
parser.add_argument('--longitude', type=float, default=0)
parser.add_argument('--latitude', type=float, default=0)
parser.add_argument('--timezone', type=str, default="UTC")

# Load configuration file and apply command-line overrides
try:
    args = parser.load_args_and_overrides(CONFIG_FILE)
except FileNotFoundError as e:
    print(e)
    print('Using defaults and command-line only')
    args = parser.parse_args()

if args.conf_export:
    print('\nConfiguration export')
    print(json.dumps(vars(args),  indent=4, sort_keys=True))

print("\nIndividual values")
print(args.elevation_m)
print(args.longitude)
print(args.latitude)
print(args.timezone)
