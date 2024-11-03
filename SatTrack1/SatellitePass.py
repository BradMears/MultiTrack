#!/usr/bin/env python3

from skyfield.api import EarthSatellite
from skyfield.toposlib import GeographicPosition
from skyfield.timelib import Time

class SatellitePass():
    # Setting this manually is hacky. There must be a better way 
    # TODO - Do some reading on python datetime and timezones
    TZ = None

    def __init__(self, 
                 pos : GeographicPosition, 
                 sat : EarthSatellite, 
                 peak_time : Time ):
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

        # Big picture for the following code. We do two searches, let's call them
        # S1 and S2. S1 goes from t0 to the peak_time and S2 goes from the 
        # peak_time to t1. The sat we're looking for may have multiple passes
        # today so we want to find the pass that is defined by the *last* rise
        # time in S1 and the *first* descent time in S2. These will straddle the
        # peak_time.

        # Step 1 - Search for events up to and including the time of interest
        # to us. The last rise_time in that list will be the one we want.    
        evt_times, events = sat.find_events(pos, t0, peak_time, altitude_degrees=0.0)
        if len(events) == 0:
            raise ValueError('Orbital period too long for window?')

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
        evt_times, events = sat.find_events(pos, peak_time, t1, altitude_degrees=0.0)
        if len(events) == 0:
            raise ValueError('Orbital period too long for window?')

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
        if self.ascend_time == None:
            print(f'Bad error {sat}')
            dt_str = self.peak_time.utc_datetime().astimezone(SatellitePass.TZ)

        if self.ascend_time == None or \
           self.descend_time == None:
            raise ValueError('Could not complete pass details')

        assert(self.ascend_time < peak_time)
        assert(peak_time < self.descend_time)

    def __lt__(self, other):
        '''Compares based on the time of breaking the horizon for each one.'''
        return self.ascend_time < other.ascend_time
    
    def __str__(self):
        s = f'{self.sat.model.satnum} {self.sat.name}\n'
        dt_str = self.ascend_time.utc_datetime().astimezone(SatellitePass.TZ)
        s += f'\t{dt_str} Rise time\n'

        dt_str = self.peak_time.utc_datetime().astimezone(SatellitePass.TZ)
        s += f'\t{dt_str} Peak time\n'
        
        dt_str = self.descend_time.utc_datetime().astimezone(SatellitePass.TZ)
        s += f'\t{dt_str} Descend time\n'

        return s
   
def upcoming_passes(observer_pos : GeographicPosition, 
                    sat : EarthSatellite, 
                    min_elevation : float, 
                    start_time : Time, 
                    end_time : Time
                    ):
    '''Return all of the upcoming passes for a satellite over a certain elevation
    in a specified timeframe. The returned tuple also contains the list of passes 
    that could not be filled in.'''
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
    failed_passes = []
    for evt_time, evt in zip(evt_times, events):
        if evt == 1:    # In Skyfield, an event of 1 is 'culminate' aka peak
            try:
                passes.append(SatellitePass(observer_pos, sat, evt_time))
            except ValueError as e:
                failed_passes.append((sat, evt_time, e))


    passes.sort()
    return passes, failed_passes
