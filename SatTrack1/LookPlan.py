#!/usr/bin/env python3
'''Calculates a look plan for a satellite pass. This is a sequence of times 
and positions that can be sent to a rotator.'''

from dataclasses import dataclass

class Pass():
    def __init__(self):
        pass

@dataclass
class RotatorSpecs:
    '''Provides the performance specs of a rotator.'''
    az_min_deg : int
    az_max_deg : int
    el_min_deg : int
    el_max_deg : int
    az_speed : float   # degrees/second

    def check(self):
        assert(self.az_min_deg < self.az_max_deg)
        assert(self.el_min_deg < self.el_max_deg)
        assert(self.az_speed > 0)

class LookPlan():
    def __init__(self, pass_info : Pass, rotator_az_speed : float):
        pass

if __name__ == '__main__':
    rotator = RotatorSpecs(az_min_deg=0, az_max_deg=540, el_min_deg=0, el_max_deg=180, az_speed=90.0/15)
    rotator.check()
    print(rotator)

