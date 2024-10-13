#!/usr/bin/env
'''Provides a basic rotator intarface that can be used for testing and as a
base class.'''

from look_plan import LookPlan

class Rotator:
    '''Provides a generic rotator interface.'''

    def __init__(self,
                 az_min_deg : int,
                 az_max_deg : int,
                 el_min_deg : int,
                 el_max_deg : int,
                 az_speed : float   # degrees/second
                 ):
        self.az_min_deg = az_min_deg 
        self.az_max_deg = az_max_deg 
        self.el_min_deg = el_min_deg
        self.el_max_deg = el_max_deg 
        self.az_speed = az_speed 
        assert(self.az_min_deg < self.az_max_deg)
        assert(self.el_min_deg < self.el_max_deg)
        assert(self.az_speed > 0)
        self.positions = []

    def execute_look_plan(self, 
                          look_plan : LookPlan,
                          immediate : bool = False) :
        '''Moves the rotator to each of the specified positions at the desired
        time. If the 'immediate' flag is True, it executes immediately.'''
        print('Executing look plan')
        print("Wow! Wasn't that great?")

    def __str__(self):
        s = f'Azimuth range = {self.az_min_deg} to {self.az_max_deg} degrees\n'
        s += f'Elevation range = {self.el_min_deg} to {self.el_max_deg} degrees\n'
        s += f'Rate of azimuth rotation = {self.az_speed} degrees/sec'
        s += str(self.positions)
        return s
    
if __name__ == '__main__':
    rotator = Rotator(az_min_deg=0, 
                      az_max_deg=540, 
                      el_min_deg=0, 
                      el_max_deg=180, 
                      az_speed=90.0/15)  # unloaded speed of the Yaesu G-5500
    print(rotator)