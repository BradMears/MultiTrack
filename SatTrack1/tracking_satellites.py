#!/usr/bin/env python3
'''Prints a list of upcoming passes for amateur radio satellites.'''

from os import environ
from datetime import datetime, timezone
import pytz
import json
from skyfield.api import load
from skyfield.api import wgs84
from skyfield.api import EarthSatellite

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
        '''Reads configuration from a text file. This is the most commone use case.'''
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

class SatWithEvents():
    '''Holds a satellite and the list of times and events that are associated 
    with it, This is not a broadly useful class but it is helpful for building
    a sorted set of passes to look at.'''

    # User code can override this if desired 
    event_names=('Ascent Event', 'Culminate', 'Descent Event')

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

class Pass():
    def __init__(self, pos, sat : EarthSatellite, peak_time):
        '''Fill in a pass given the time it peaks (or 'culminates')'''
        # This is not efficient and it has belt, suspenders, and duct tape
        # since I am still exploring the Skyfield API.    
        self.sat = sat
        self.peak_time = peak_time
        self.ascend_time = None # These better be explicitly set before we're done 
        self.descend_time = None

        # How wide a timeframe should we examine? If we make it too small, we 
        # may not get the time when it goes above or below the horizon. If we 
        # make it too big, we may burn a lot of processing time.
        # I would like to base this on the sat's orbital period but I don't
        # know an easy way to calculate that right now. For now, I'm using
        # a smallish value since I'm interested in LEO objects
        window_in_minutes = 120 / (60 * 24)
        t0 = peak_time - window_in_minutes
        t1 = peak_time + window_in_minutes

        # Step 1 - Search for events up to and including the time of interest
        # to us. The last rise_time in that list will be the one we want.    
        evt_times, events = sat.find_events(qth, t0, peak_time, altitude_degrees=0.0)
        if len(events) == 0:
            raise ValueError('Orbital period too long?')

        # This is a paranoia loop. Take it out after it has passed a few times 
        prev_time = evt_times[0] - 1 # Dummy for first comparison 
        for evt_time, event in zip(evt_times, events):
            assert(prev_time < evt_time)  # Do we understand the return values correctly or not?
            prev_time = evt_time

        # Since the event times are sorted in ascending time, the last rise time is the one we want
        for evt_time, event in zip(reversed(evt_times), reversed(events)):
            if event == 0:   # Rising event
                self.ascend_time = evt_time
                break

        # Step 2 - Search for starting at the time of interest. The first descent
        # in that list will be the one we want.    
        evt_times, events = sat.find_events(qth, peak_time, t1, altitude_degrees=0.0)
        if len(events) == 0:
            raise ValueError('Orbital period too long?')

        # This is a paranoia loop. Take it out after it has passed a few times 
        prev_time = evt_times[0] - 1  # Dummy for first comparison 
        for evt_time, event in zip(evt_times, events):
            assert(prev_time < evt_time)  # Do we understand the return values correctly or not?
            prev_time = evt_time

        # Since the event times are sorted in ascending time, the first descent time is the one we want
        for evt_time, event in zip(evt_times, events):
            if event == 2:   # Rising event
                self.descend_time = evt_time
                break

        # We better have found both the events we were looking for and they better
        # be in the right time order. Otherwise something is wrong
        assert(self.ascend_time != None)
        assert(self.descend_time != None)
        assert(self.ascend_time < peak_time)
        assert(peak_time < self.descend_time)

    def __lt__(self, other):
        '''Compares based on the time of breaking the horizon for each one.'''
        return self.ascend_time < other.ascend_time
    
    def __str__(self):
        s = f'{self.sat.model.satnum} {self.sat.name}\n'
        dt_str = self.ascend_time.utc_datetime().astimezone(TZ)
        s += f'\t{dt_str} Rise time\n'

        dt_str = self.peak_time.utc_datetime().astimezone(TZ)
        s += f'\t{dt_str} Peak time\n'
        
        dt_str = self.descend_time.utc_datetime().astimezone(TZ)
        s += f'\t{dt_str} Descend time\n'

        return s

    

from typing import List
from skyfield.toposlib import GeographicPosition
def upcoming_passes(observer_pos : GeographicPosition, 
                   sat : EarthSatellite, 
                   min_elevation : float, 
                   start_time, 
                   end_time
                   ) -> List[Pass]:
    '''Return all of the upcoming passes for a satellite over a certain elevation in specified timeframe.'''
    t0 = start_time
    t1 = end_time

    ''' Calling find_events() can return a set like this. We need to turn this 
    into multiple passes.
    According to https://rhodesmill.org/skyfield/earth-satellites.html:
    "Beware that events might not always be in the order rise-culminate-set. 
    Some satellites culminate several times between rising and setting."

     16     32953 YUBILEINY (RS-30)                   
        2024-10-11 11:11:42.644698-06:00 Rise above 30°
        2024-10-11 11:14:50.491074-06:00 Culminate  
        2024-10-11 11:17:57.316252-06:00 Set below 30°                                                   
        2024-10-11 13:07:54.790948-06:00 Rise above 30°                                                  
        2024-10-11 13:11:39.356618-06:00 Culminate
        2024-10-11 13:15:22.755607-06:00 Set below 30° 
    '''
    evt_times, events = sat.find_events(observer_pos, t0, t1, altitude_degrees=min_elevation)

    # The list of events from find_events() will contain 0 or more culminate 
    # events that indicate the sat is at its peak. Each of these peaks represents
    # a unique pass. Send that info to the Pass constructor so it can fill in the
    # details.
    passes = []
    for evt_time, evt in zip(evt_times, events):
        if evt == 1:    # In Skyfield, an event of 1 is 'culminate' aka peak
            try:
                passes.append(Pass(observer_pos, sat, evt_time))
            except ValueError as e:
                dt_str = evt_time.utc_datetime().astimezone(TZ)
                print(f"Didn't add pass for {sat} at {dt_str}\n{e}")

    passes.sort()
    print(f'################## Generarated {len(passes)} passes for {sat}')
    return passes


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

    ts = load.timescale()
    t = ts.now()
    dt = t.utc_datetime()
    print(f"Local time {dt.astimezone(TZ).isoformat()}")

    amsats_json = load_from_file_or_url('amateur')
    amsats = [EarthSatellite.from_omm(ts, fields) for fields in amsats_json]

    qth = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m = elev)

    print(f"Upcoming passes for : {qth}")
    print(f'All times in {TZ} timezone')
    print()

    for sat in amsats:
        passes = upcoming_passes(qth, sat, 30.0, t, t+12/24)
        for sat_pass in passes:
            print(sat_pass)

    exit()

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
    sat = entry.sat
    SatWithEvents.event_names = ('Above horizon', 'Culminate', 'Below horizon')
    evt_time, events = sat.find_events(qth, t0, t1, altitude_degrees=0.0)
    entry = SatWithEvents(sat, evt_time, events)
    print(entry)

    # Print the look plan
    # Current output format
    # <Time tt=2460594.4939523726> Az = 131deg 31' 06.6" Elev = 15deg 55' 13.8"
    difference = sat - qth
    t0 = entry.evt_time[0]
    t1 = entry.evt_time[-1]
    look_time = t0
    time_step = 1 / (24 * 60)   # 1 minute
    while look_time.utc_datetime() <= t1.utc_datetime():
        topocentric = difference.at(look_time)
        dt_str = look_time.utc_datetime().astimezone(TZ)
        alt, az, distance = topocentric.altaz()
        #if alt.degrees > 0.0:
        print(f'{dt_str} Az = {az.degrees:7.2f} Elev = {alt.degrees:7.2f} ')
        look_time += time_step

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
