#!/usr/bin/env python3
'''Prints a list of upcoming passes for amateur radio satellites.'''

from os import environ
from datetime import datetime, timezone
import pytz
import json
from skyfield.api import load
from skyfield.api import wgs84
from skyfield.api import EarthSatellite

# Observer coordinates
lat, lon, elev = 38.9596, -104.7695, 2092

# Set the timezone and get the current time in skyfield format and in
# regular python datetime
try:
    TZ_STRING = environ['TZ']
except KeyError:
    TZ_STRING = 'America/Denver'
TZ = pytz.timezone(TZ_STRING)

ts = load.timescale()
t = ts.now()
dt = t.utc_datetime()
print(f"Local time {dt.astimezone(TZ).isoformat()}")

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

amsats_json = load_from_file_or_url('amateur')
amsats = [EarthSatellite.from_omm(ts, fields) for fields in amsats_json]

qth = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m = elev)

print(f"Upcoming passes for : {qth}")
print(f'All times in {TZ} timezone')
print()

class SatWithEvents():
    '''Holds a satellite and the list of times and events that are associated 
    with it, This is not a broadly useful class but it is helpful for building
    a sorted set of passes to look at.'''

    # User code can override this if desired 
    event_names=['Ascent Event', 'Culminate', 'Descent Event']

    def __init__(self, sat, evt_time, events):
        self.sat = sat
        self.evt_time = evt_time
        self.events = events

    def __lt__(self, other):
        '''Compares based solely on the time of the first event for each one.'''
        return self.evt_time[0] < other.evt_time[0]
    
    def __str__(self):
        assert(len(SatWithEvents.event_names) == 3)
        s = f'{self.sat.model.satnum} {self.sat.name}\n'
        for ti, event in zip(self.evt_time, self.events):
            dt_str = ti.utc_datetime().astimezone(TZ)
            s += f'\t{dt_str} {SatWithEvents.event_names[event]}\n'
        
        return s

# Find all satellites with passes over a certain elevation happening in 
# the upcoming few hours
t0 = t
t1 = t0 + 4/24 # 4 hours
#t1 = t0 + 2/24 #2 hours
sats_with_events = []
SatWithEvents.event_names = 'rise above 30°', 'Culminate', 'set below 30°'
for sat in amsats:
    evt_time, events = sat.find_events(qth, t0, t1, altitude_degrees=30.0)
    if len(events) > 0:
        sats_with_events.append(SatWithEvents(sat, evt_time, events))

# Sort that list based on date & time
sats_with_events.sort()
for ii, entry in enumerate(sats_with_events):
    print(f'{ii+1:3}\t{entry}')

# Let the user select a pass to track
pass_num = 0
while not(0 < pass_num <= len(sats_with_events)):
    pass_num = int(input("Choose a pass to watch: ")) 
pass_num -= 1 # put it back to a zero index

entry = sats_with_events[pass_num]
print(f"You selected {entry.sat.name}")
print(entry)

print('Horizon to horizon times')
window_in_minutes = 30 / (24 * 60)
t0 = entry.evt_time[0] - window_in_minutes
t1 = entry.evt_time[-1] + window_in_minutes
SatWithEvents.event_names = 'Above horizon', 'Culminate', 'Below horizon'
evt_time, events = entry.sat.find_events(qth, t0, t1, altitude_degrees=0.0)
entry = SatWithEvents(entry.sat, evt_time, events)
print(entry)

if False:
    pass
    '''
    difference = sat - qth
    days = t - sat.epoch

        print(f'sat = {sat.name}')
        event_names = 'rise above 30°', 'culminate', 'set below 30°'
        for ti, event in zip(evt_time, events):
            name = event_names[event]
            print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)
            for m in range(20):
                new_t = t0 + (m / (24*60))
                topocentric = difference.at(t)
                alt, az, distance = topocentric.altaz()
                print(f'{m} {alt} {az}')
    
    break
    '''
        
    '''
    if abs(days) > 2 and not refreshed:
        satellites = load.tle(stations_url, reload=True)
        refreshed = True
        satellite = satellites[sat]
        difference = satellite - qth
        days = t - satellite.epoch

    i += 1
    print("Processing [%02d] %s: %.3f days away from epoch" % (i, sat, days))
    res += "\n%s: %.3f days away from epoch\n" % (sat, days)
    res += "%-16s  %3s  %-4s  %5s\n" % ("DATETIME",
        "ALT",
        "AZIM",
        "KM",)

    sep = True
'''
'''
    for hh in range(24):

        for mm in range(60):

            t = ts.utc(year, month, day, hh, mm)
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()

            if alt.degrees < -0.5:
                sep = True
            else:
                if sep:
                    res += "%s\n" % ("-" * 34)
                    sep = False

                res += "%s  %2d°  %3d°  %5d\n" % (t.utc_strftime('%Y-%m-%d %H:%M'),
                    round(alt.degrees),
                    round(az.degrees),
                    round(distance.km),)

with open(sat_file, 'w', encoding='utf-8') as outfile:
    outfile.write(res)

print("Writing satellite times to: %s" % sat_file)
'''
