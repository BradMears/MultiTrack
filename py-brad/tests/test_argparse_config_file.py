'''pytest for argparse_config_file.'''

import pytest
import argparse_config_file
import os

# This file tests a combination of using default values, just values from a 
# configfile, values from a partial config file, values from a config file 
# overriden by command-line parameters.

@pytest.fixture
def parser():
    # Define the set of command-line arguments
    test_parser = argparse_config_file.ArgumentParserWithConfig(description=__doc__)
    test_parser.add_argument('--conf_export', action='store_true')
    test_parser.add_argument('--latitude', type=float, default=10.0)
    test_parser.add_argument('--longitude', type=float, default=20.0)
    test_parser.add_argument('--elevation_m', type=float, default=30.0)
    test_parser.add_argument('--timezone', type=str, default="UTC")
    return test_parser

@pytest.fixture
def output_file_partial(tmp_path):
    # Create a partial config file that can be loaded for a test
    filepath = os.path.join(tmp_path,'argparse_test_partial.txt')
    with open(filepath, 'w+') as f:
        f.write(
            '''
            # Data generated by unit test
            # Only sets some of the fields
            latitude = 45.67
            elevation_m = 2134
            ''')
        
    return filepath

@pytest.fixture
def output_file(tmp_path):
    # Create a config file that can be loaded for a test
    filepath = os.path.join(tmp_path,'argparse_test.txt')
    with open(filepath, 'w+') as f:
        f.write(
            '''
            # Data generated by unit test
            latitude = 12.345
            longitude = -106
            elevation_m = 1001
            timezone = "America/Denver"
            ''')
        
    return filepath

# In the following tests, we don't *have* to pass an empty list to parse_args()
# and load_args_and_overrides() but if we don't, then everything blows up if we 
# try to pass any arguments to pytest because the argparse library will use
# sys.argv if you don't provide any args.

def test_default_values(parser):
    # Confirm we can still use this as an argparse.ArgumentParser
    args = parser.parse_args([])
    assert args.latitude == 10.0
    assert args.longitude == 20.0
    assert args.elevation_m == 30.0
    assert args.timezone == 'UTC'


def test_config_file_partial(output_file_partial, parser):
    args = parser.load_args_and_overrides(output_file_partial, [])
    assert args.latitude == 45.67
    assert args.longitude == 20.0
    assert args.elevation_m == 2134
    assert args.timezone == 'UTC'
 

def test_config_file(output_file, parser):
    args = parser.load_args_and_overrides(output_file, [])
    assert args.latitude == 12.345 
    assert args.longitude == -106
    assert args.elevation_m == 1001
    assert args.timezone == 'America/Denver'
 
 
def test_config_file_and_overrides(output_file, parser):
    args = parser.load_args_and_overrides(output_file,['--longitude=23.1', '--timezone=Elsewhere'])
    assert args.latitude == 12.345 
    assert args.longitude == 23.1
    assert args.elevation_m == 1001
    assert args.timezone == 'Elsewhere'
 
def test_file_not_found(parser):
    with pytest.raises(FileNotFoundError):
        args = parser.load_args_and_overrides("non-existent-file.txt", [])
    assert(True)

   