#!/usr/bin/env python3
'''Extends argparse to also read values from a configuration file.'''

import argparse
import toml

class ArgumentParserWithConfig(argparse.ArgumentParser):
    '''Extends argparse to also read values from a configuration file.'''

    def load_args_and_overrides(self, config_file, *argv):
        '''Read from the specified configuration file, if it exists, and then 
        apply command-line args as overrides.'''

        try:
            toml_data = toml.load(config_file)
            self.set_defaults(**toml_data)
        except FileNotFoundError:
            e = FileNotFoundError(f'Configuration file {config_file} not found. Correct filename or try using just parse_args.')
            raise e

        # Override config file values with command line values
        args = self.parse_args(*argv)
        return args

