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
    enforce which settings are supposed to be present. October 2024'''
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

    # Print them out in order of time
    all_passes.sort()
    pass_num = 1
    print(f"Upcoming passes for : {obs_pos}")
    print(f'All times in {TZ} timezone')
    print()
    for sat_pass in all_passes:
        print(f'{pass_num} {sat_pass}')
        pass_num += 1

    # Let the user select a pass to track
    pass_num = 0
    while not(0 < pass_num <= len(all_passes)):
        pass_num = int(input("Choose a pass to watch: ")) 
    pass_num -= 1 # put it back to a zero index

    sat_pass = all_passes[pass_num]
    print(f"You selected {sat_pass.sat.name}")
    print(sat_pass)
    sat = sat_pass.sat

    # Create and print the look plan
    time_step = 1 / (24 * 60)   # 1 minute
    look_plan = LookPlan(obs_pos, sat_pass, time_step=time_step)
    print(look_plan)

    rotator = Rotator(az_min_deg=0, 
                    az_max_deg=540, 
                    el_min_deg=0, 
                    el_max_deg=180, 
                    az_speed=90.0/15)  # unloaded speed of the Yaesu G-5500
    
    rotator.execute_look_plan(look_plan)
