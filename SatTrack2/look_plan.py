#!/usr/bin/env python3
'''Calculates a look plan for a satellite pass. This is a sequence of times 
and positions that can be sent to a rotator.'''

from datetime import datetime
from typing import List
from skyfield.api import EarthSatellite, Time
from skyfield.api import wgs84
from SatellitePass import SatellitePass
from rotator_position import RotatorPosition

class LookPlan():
    '''Holds everything you need to command a rotator to follow a satellite pass.'''

    TZ = None

    def __init__(self, 
                 obs_pos : wgs84.latlon,   # observer poosition on Earth
                 sat_pass : SatellitePass, 
                 time_step : float, # decimal fraction of a day 
                 ):
        self.obs_pos = obs_pos
        self.sat_pass = sat_pass
        difference = sat_pass.sat - obs_pos
        end_time = sat_pass.descend_time.utc_datetime()
        look_time = sat_pass.ascend_time
        self.rotator_positions = []
        while look_time.utc_datetime() <= end_time:
            topocentric = difference.at(look_time)
            alt, az, distance = topocentric.altaz()
            self.rotator_positions.append(RotatorPosition(look_time.utc_datetime(), az, alt))
            look_time += time_step

    def __str__(self):
        sat = self.sat_pass.sat
        s = f'LookPlan for {sat.name} ({sat.model.satnum}) from {self.obs_pos}\n'
        for pos in self.rotator_positions:
            dt_str = pos.look_time.astimezone(LookPlan.TZ)
            s += f'{dt_str} Az = {pos.az.degrees:6.2f} Elev = {pos.el.degrees:6.2f}\n'
            #s += f'{dt_str} Az = {pos.az.degrees:6.2f} Elev = {pos.alt.degrees:6.2f} '

        return s

if __name__ == '__main__':
    rotator = Rotator(az_min_deg=0, az_max_deg=540, el_min_deg=0, el_max_deg=180, az_speed=90.0/15)
    print(rotator)

