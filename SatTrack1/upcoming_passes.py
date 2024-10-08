#!/usr/bin/env python3
'''Prints a list of upcoming passes for amateur radio satellites.'''

import json
from skyfield.api import load
from skyfield.api import wgs84
from skyfield.api import EarthSatellite

ts = load.timescale()
t = ts.now()

# Observer coordinates
lat, lon, elev = 38.9596, -104.7695, 2092

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
#print(json.dumps(amsats_json, indent=4))
#print('Loaded', len(amsats), 'satellites')

qth = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m = elev)
dt = t.utc_datetime()
print(dt)

#for sat in amsats:
#    print(f'{sat.name} {sat.model.satnum}')

print(f"Upcoming passes for : {qth}\n")
print("Date:", "-".join([str(dt.year), str(dt.month), str(dt.day)]), "\n")

t0 = t
t1 = t0 + 0.25 # 6 hours
for sat in amsats:

    difference = sat - qth
    days = t - sat.epoch

    #print(f'diff 1= {difference.at(t)}')
    #print(f'diff 2= {(qth - sat).at(t)}')

    aos_time, events = sat.find_events(qth, t0, t1, altitude_degrees=30.0)
    if len(events) > 0:
        print(f'sat = {sat.name}')
        event_names = 'rise above 30°', 'culminate', 'set below 30°'
        for ti, event in zip(aos_time, events):
            name = event_names[event]
            print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)


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
