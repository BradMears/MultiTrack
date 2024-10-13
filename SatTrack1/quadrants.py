#!/usr/bin/env python3
'''Prints a list of upcoming passes for amateur radio satellites.'''

from os import environ
from datetime import datetime, timezone
import pytz
import json
from skyfield.api import load
from skyfield.api import wgs84
from skyfield.api import EarthSatellite
from SatellitePass import SatellitePass, upcoming_passes
from rotator_position import RotatorPosition
from look_plan import LookPlan
from rotator import Rotator

class Globals:
    '''Encapsulates a name/value config file and turns it into a map of
    variables that can be used globally. Not sure if I like this design
    or not. It is an experiment. A downside to it is that it doesn't
    enforce which settings aare supposed to be present. October 2024'''
    vars = {}
    
    @staticmethod
    def init(readable):
        '''Don't call this directly. Call one of the init_from_blah() methods.'''
        myvars = {}
        for line in readable:
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            name, var = line.partition("=")[::2]
            name = name.strip()
            try:
                myvars[name] = float(var)
            except ValueError:
                myvars[name] = var.strip()

        Globals.vars = type("Names", (), myvars)

    @staticmethod
    def init_from_file(filename : str ):
        '''Reads configuration from a text file. This is the most common use case.'''
        cal_file = open(filename, "r")
        Globals.init(cal_file)

    @staticmethod
    def init_from_string(cls, raw_string : str ):
        '''Reads configurations from a text string. Useful for unit testing.'''
        readable = StringIO(raw_string)
        Globals.init(readable)

def load_from_file_or_url(group_name, max_days=7.0):
    '''Loads Satellite data. First looks for a local file. If that doesn't 
    exist or is older than max_days, goes to the Celestrak site.'''
    filename = f'{group_name}.json'  # custom filename, not 'gp.php'

    base = 'https://celestrak.org/NORAD/elements/gp.php'
    url = base + f'?GROUP={group_name}&FORMAT=json'

    if not load.exists(filename) or load.days_old(filename) >= max_days:
        print("File doesn't exist or is too old. Downloading")
        load.download(url, filename=filename)

    with load.open(filename) as f:
        raw_json = json.load(f)

    return raw_json

if __name__ == "__main__":
    Globals.init_from_file('observer.txt')

    # Observer coordinates
    lon = Globals.vars.longitude
    lat = Globals.vars.latitude
    elev = Globals.vars.elevation_m

    # Set the timezone and get the current time in skyfield format and in
    # regular python datetime
    try:
        TZ_STRING = environ['TZ']
    except KeyError:
        TZ_STRING = Globals.vars.timezone
    TZ = pytz.timezone(TZ_STRING)
    SatellitePass.TZ = TZ
    RotatorPosition.TZ = TZ
    LookPlan.TZ = TZ

    ts = load.timescale()
    t = ts.now()
    dt = t.utc_datetime()
    print(f"Local time {dt.astimezone(TZ).isoformat()}")

    amsats_json = load_from_file_or_url('amateur')
    amsats = [EarthSatellite.from_omm(ts, fields) for fields in amsats_json]

    obs_pos = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m = elev)

    # Find all upcoming passes over 30 degrees in the desired timeframe
    t_end = t + 4 / 24
    all_passes = []
    all_failed_passes = []
    for sat in amsats:
        sat_passes, failed_passes = upcoming_passes(obs_pos, sat, 30.0, t, t_end)
        all_passes += sat_passes
        all_failed_passes += failed_passes

    # If there were any passes that didn't get filled in, let the user know
    for failure in all_failed_passes:
        dt_str = failure[1].utc_datetime().astimezone(SatellitePass.TZ)
        print(f'Did not fill in pass for {failure[0]} at {dt_str}')
        print(f'\t{failure[2]}')
    print()

    def quadrant(angle : float) -> int:
        if angle <= 90:
            return 1
        elif angle <= 180:
            return 2
        elif angle <= 270:
            return 3
        elif angle <= 360:
            return 4
        assert(False)

    time_step = 1 / (24 * 60)   # 1 minute
    for sat_pass in all_passes:
        sat = sat_pass.sat
        look_plan = LookPlan(obs_pos, sat_pass, time_step=time_step)
        mid_pos = int(len(look_plan.rotator_positions)/2)
        beg_ang = look_plan.rotator_positions[0].az.degrees
        mid_ang =  look_plan.rotator_positions[mid_pos].az.degrees
        end_ang = look_plan.rotator_positions[-1].az.degrees
        print(f'{sat.name}')
        print(f'\tBeg ang {beg_ang:6.2f} {quadrant(beg_ang)}')
        print(f'\tMid ang {mid_ang:6.2f} {quadrant(mid_ang)}')
        print(f'\tEnd ang {end_ang:6.2f} {quadrant(end_ang)}')
