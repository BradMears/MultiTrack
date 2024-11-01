#!/usr/bin/ev python3
'''Provides  a simple dataclass that contains the time and position that we will
use to aim a rotator at a satellite.'''
from datetime import datetime
from dataclasses import dataclass

@dataclass
class RotatorPosition:
    '''Internal class for holding rotator positions.'''
    look_time : datetime
    az : float
    el : float

    # This is the second time I've propagated this hack. It needs to die
    TZ = None

    def __str__(self):
        dt_str = self.look_time.utc_datetime().astimezone(RotatorPosition.TZ)
        s = f'{dt_str} Az: {self.az:6.2}  El: {self.el:6.2}'
        return s

    def __lt__(self, other):
        return self.look_time < other.look_time
    