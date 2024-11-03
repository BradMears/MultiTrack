#!/usr/bin/env python3

'''Prints a list of upcoming passes for amateur radio satellites.'''

from datetime import datetime, timezone
import pytz
import json
from skyfield.api import load
from skyfield.api import wgs84
from skyfield.api import EarthSatellite
from SatellitePass import SatellitePass, upcoming_passes
import argparse_config_file

CONFIG_FILE='observer.txt'

# Define the set of command-line arguments
parser = argparse_config_file.ArgumentParserWithConfig(description=__doc__)
parser.add_argument('--conf_export', action='store_true')
parser.add_argument('--elevation_m', type=float, default=0)
parser.add_argument('--longitude', type=float, default=0)
parser.add_argument('--latitude', type=float, default=0)
parser.add_argument('--timezone', type=str, default="UTC")
parser.add_argument('--max_passes', type=int, default=99999)


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
    # Load configuration file and apply command-line overrides
    try:
        args = parser.load_args_and_overrides(CONFIG_FILE)
    except FileNotFoundError as e:
        print(e)
        print('Using defaults and command-line only')
        args = parser.parse_args()

    # Observer coordinates
    lon = args.longitude
    lat = args.latitude
    elev = args.elevation_m

    # Set the timezone and get the current time in skyfield format and in
    # regular python datetime
    TZ_STRING = args.timezone
    TZ = pytz.timezone(TZ_STRING)
    SatellitePass.TZ = TZ

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
    max_passes = min(args.max_passes, len(all_passes))
    print(f"Upcoming passes for : {obs_pos}")
    print(f'All times in {TZ} timezone')
    print()
    for sat_pass in all_passes:
        print(f'{pass_num} {sat_pass}')
        pass_num += 1
        if pass_num > max_passes:
            break

    # Let the user select a pass to track
    pass_num = 0
    while not(0 < pass_num <= max_passes):
        pass_num = int(input("Choose a pass to watch: ")) 
    pass_num -= 1 # put it back to a zero index

    sat_pass = all_passes[pass_num]
    print(f"You selected {sat_pass.sat.name}")
    print(sat_pass)
    sat = sat_pass.sat

    # Print the look plan
    difference = sat_pass.sat - obs_pos
    t0 = sat_pass.ascend_time
    t1 = sat_pass.descend_time
    look_time = t0
    time_step = 1 / (24 * 60)   # 1 minute
    while look_time.utc_datetime() <= t1.utc_datetime():
        topocentric = difference.at(look_time)
        dt_str = look_time.utc_datetime().astimezone(TZ)
        alt, az, distance = topocentric.altaz()
        print(f'{dt_str} Az = {az.degrees:6.2f} Elev = {alt.degrees:6.2f} ')
        look_time += time_step
