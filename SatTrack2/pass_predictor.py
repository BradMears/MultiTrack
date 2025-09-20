#!/usr/bin/env python3

'''Prints a list of upcoming passes for various satellites. Arguments can be 
specified on the command-line or in the config-file observer.txt' The command-line
takes precedence over the config-file.'''

from datetime import datetime, timezone, timedelta
import pytz
import json
from skyfield.api import load
from skyfield.api import Loader
from skyfield.api import wgs84
from skyfield.api import EarthSatellite
from skyfield.iokit import parse_tle_file
from SatellitePass import SatellitePass, upcoming_passes
import argparse_config_file

CONFIG_FILE = 'observer.txt'

# Define the set of command-line arguments
# Since we're using argparse_config_file, all of these can be specified in the config file
parser = argparse_config_file.ArgumentParserWithConfig(description=__doc__)
#parser.add_argument('--conf_export', action='store_true')
parser.add_argument('--elevation_m', type=float, default=0, help = 'Elevation in meters above sea-level of observer')
parser.add_argument('--longitude', type=float, default=0, help = 'Longitude of observer in decimal degrees')
parser.add_argument('--latitude', type=float, default=0, help = 'Latitude of observer in decimal degrees')
parser.add_argument('--timezone', type=str, default="UTC", help = 'Timezone to use for displaying time')
parser.add_argument('--min_angle', type=int, default=30, help = 'Minimum angle in degrees above the horizon')
parser.add_argument('--max_passes', type=int, default=99999, help = 'Max number of passes to display')
parser.add_argument('--min_range', type=int, default=100, help='Lower range limit to consider')
parser.add_argument('--max_range', type=int, default=6000, help='Upper range limit to consider')
parser.add_argument('--max_hours', type=float, default=4, help = 'Maximum look-ahead time')
parser.add_argument('--sat_name', type=str, default="", help = 'Only show satellites whose name starts with this string')
parser.add_argument('--cat_number', type=int, default="-1", help = 'Only show the satellite with this catalog ID')
parser.add_argument('--tle_file', type=str, default="", help = 'Name of TLE file to use')

"""
def load_from_file_or_url(group_name, max_days=7.0):
    '''Loads Satellite data. First looks for a local file. If that doesn't 
    exist or is older than max_days, goes to the Celestrak site.'''
    filename = f'{group_name}.json'  # custom filename, not 'gp.php'

    # You can use https on the following request but my work laptop complains about a self-signed certificate
    # when I do that. Using plain http works fine.
    base = 'http://celestrak.org/NORAD/elements/gp.php'
    url = base + f'?GROUP={group_name}&FORMAT=json'
    #url = 'https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/1641,01361,05398,09931,13154,16496,16792,16882,20262,20663,20666,20705,23581,24748,25050,25544,25724,30794,41182,41591,43611,41793,40940,43432,36744,42691,41944,41034,29495,42695,37933/orderby/TLE_LINE1%20ASC/format/3le'

    if not load.exists(filename) or load.days_old(filename) >= max_days:
        print("File doesn't exist or is too old. Downloading")
        load.download(url, filename=filename)

    with load.open(filename) as f:
        raw_json = json.load(f)

    return raw_json
"""

if __name__ == "__main__":
    #load_from_file_or_url(group_name='amateur', max_days=7.0)
    #exit()

    # Load configuration file and apply command-line overrides
    try:
        args = parser.load_args_and_overrides(CONFIG_FILE)
    except FileNotFoundError as e:
        print(e)
        print('Using defaults and command-line only')
        args = parser.parse_args()

    # Set the timezone and get the current time in skyfield format and in
    # regular python datetime
    TZ_STRING = args.timezone
    TZ = pytz.timezone(TZ_STRING)
    SatellitePass.TZ = TZ

    ts = load.timescale()
    t = ts.now()
    dt = t.utc_datetime()
    print(f"Time {dt.astimezone(TZ).isoformat()} ({TZ_STRING})", flush=True)

    tz = pytz.timezone('UTC')

    assert(0 < args.max_hours < 24)
    assert(0 < args.min_angle <= 90)

    # Read the TLE file
    myloader = Loader('./skyfield-data')
    #group='Starlink'
    #group='amateur'
    group='radar'
    frmt='tle'
    base = 'http://celestrak.org/NORAD/elements/gp.php'
    url = base + f'?GROUP={group}&FORMAT={frmt}'
    with myloader.open(url, filename=f'{group}.{frmt}') as f:
        sat_list = list(parse_tle_file(f, ts))
    print(f'Loaded {len(sat_list)} satellites', flush=True)

    if (args.cat_number != -1) and (args.sat_name != ''):
        print("Specifying the catalog number and the satellite name prefix at the same time doesn't make sense.")
        print("Are you sure you know what you're doing?")

    # Select only satellites whose name starts with the specified string
    prefix = args.sat_name.lower()
    if args.sat_name != '':
        sat_list = [s for s in sat_list if s.name.lower().startswith(prefix)]
        print(f'Filtered down to {len(sat_list)} satellites based on name prefix', flush=True)

    # Select only the satellite with the specified catalog number
    if args.cat_number != -1:
        sat_list = [s for s in sat_list if s.model.satnum == args.cat_number]
        print(f'Filtered down to {len(sat_list)} satellites based on catalog number', flush=True)

    # Observer coordinates
    obs_pos = wgs84.latlon(latitude_degrees=args.latitude, 
                           longitude_degrees=args.longitude, 
                           elevation_m = args.elevation_m)

    # Find all upcoming passes over the minimum angle in the desired timeframe
    # Find the upcoming passes for all satellites of interest
    print('########## Finding upcoming passes', flush=True)
    all_passes = []
    t_end = t + args.max_hours / 24
    for sat in sat_list:
        sat_passes = upcoming_passes(obs_pos, sat, args.min_angle, t, t_end)
        all_passes += sat_passes

    print(f'{len(all_passes)} passes found')

    # Select passes based on time window and maximum range
    print('########## Time and distance filter', flush=True)
    passes_in_range = []
    for sat_pass in all_passes:
        # Filter out the DEBs since they are not of interest
        if 'DEB' in sat_pass.sat.name:
            continue

        difference = sat_pass.sat - obs_pos
        t0 = sat_pass.ascend_time
        t1 = sat_pass.descend_time
        look_time = t0
        time_step = 1 / (24 * 60)   # 1 minute
        # If the rise time is at least one minute in the future
        # then loop through the entire pass time_step minutes at a time
        if t0.utc_datetime() > dt + timedelta(minutes=1):
            in_range = True
            while look_time.utc_datetime() <= t1.utc_datetime():
                topocentric = difference.at(look_time)
                dt_str = look_time.utc_datetime().astimezone(TZ)
                alt, az, distance = topocentric.altaz()
                # If the range at any time step exceeds the allowed range, drop this guy
                if distance.km < args.min_range or distance.km > args.max_range:
                    in_range = False
                    break
                look_time += time_step
            if in_range:
                passes_in_range.append(sat_pass)

    # Whatever remains is the set we're interested in
    all_passes = passes_in_range
    print(f'{len(all_passes)} passes remaining after filtering')

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

    while True:
        # Let the user select a pass to track
        if len(all_passes) == 0:
            print("No passes found")
            exit(0)

        pass_num = 0
        while not(0 < pass_num <= max_passes):
            pass_num = int(input("Choose a pass to watch: ")) 
        pass_num -= 1 # put it back to a zero index

        sat_pass = all_passes[pass_num]
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
            print(f'{dt_str} Az = {az.degrees:6.2f} Elev = {alt.degrees:6.2f} Distance = {distance.km:6.2f}')
            look_time += time_step

        if input('\nLook at another? (y/n) ' ) == 'y':
            print()
            continue
        else:
            break
