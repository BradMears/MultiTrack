'''
Copyright 2018 Jari Perkiömäki OH6BG.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

#
# KE0YAL's modifications
#

import json
from skyfield.api import load, load_file
from skyfield.api import Topos
from skyfield.api import EarthSatellite

ts = load.timescale()
t = ts.now()

print(f'ts = {ts}')
print(f't = {t}')
# Observer coordinates
lat, lon = 38.9596, -104.7695
# Observer date
year, month, day = 2024, 10, 9

#i, refreshed, sat_list = 0, False, []
#sat_file = "amateur_satellite_times_%s-%s-%s.txt" % (year, month, day)
#stations_url = 'https://www.celestrak.com/NORAD/elements/amateur.txt'

max_days = 7.0         # download again once 7 days old
filename = 'amateur.json'  # custom filename, not 'gp.php'

base = 'https://celestrak.org/NORAD/elements/gp.php'
url = base + '?GROUP=amateur&FORMAT=json'

if not load.exists(filename) or load.days_old(filename) >= max_days:
    load.download(url, filename=filename)

with load.open(filename) as f:
    data = json.load(f)

amsats = [EarthSatellite.from_omm(ts, fields) for fields in data]
print('Loaded', len(amsats), 'satellites')
print(json.dumps(data, indent=4))

qth = Topos(lat, lon)

res = "AMATEUR SATELLITE TIMES FOR LOCATION: %s, %s\n" % (lat, lon)
print(res)
print("Date:", "-".join([str(year), str(month), str(day)]), "\n")

#print(f'satellites = {satellites}')
#for k, v in satellites.items():
#    print(f'{k} (key)\t{v}')

'''
for sat in satellites:

    if isinstance(sat, int):
        continue

    satellite = satellites[sat]
    print(f'sat = {sat}  satellite = {satellite}')
    sid = str(satellite).rsplit(' ', 2)[1].split("=")[1]

    if sid not in sat_list:
        sat_list.append(sid)
    else:
        continue

    difference = satellite - qth
    days = t - satellite.epoch

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
