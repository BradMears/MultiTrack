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
                 evt_ndx, 
                 peak_time, 
                 evt_times, 
                 events ): 
        '''Fill in a pass given the time it peaks (or 'culminates')'''
        self.sat = sat
        self.peak_time = peak_time
        self.ascend_time = None # These better be explicitly set before we're done 
        self.descend_time = None

        # Big picture for the following code. We do two searches, one searching 
        # backwards from the peak event to find the corresponding rise event and
        # the other searching forwards from the peak event to find the 
        # corresponding descent event.
        # Yes, the following code could and should be written more pythonically
        # using zip, enumerate, and reverse. But I'm in a hurry and didn't want
        # to take the time to fiddle with that. This was quick and easy.
        for ndx_base in range(evt_ndx+1):
            ndx = evt_ndx - ndx_base
            if events[ndx] == 0:   # Rising event
                self.ascend_time = evt_times[ndx]
                break

        for ndx in range(evt_ndx, len(events)):
            if events[ndx] == 2:   # Descent event
                self.descend_time = evt_times[ndx]

        # We better have found both the events we were looking for and they better
        # be in the right time order. Otherwise something is wrong
        if self.descend_time == None:
            raise ValueError(f'No set time found in window for {sat}')
        
        if self.ascend_time == None:
            raise ValueError(f'No rise time found in window for {sat}')

        if self.ascend_time > self.descend_time:
            raise ValueError(f'Rise time and set time are out of order for {sat}')

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

    # The list of events from find_events() will contain zero or more culminate 
    # events that indicate the sat is at its peak. Each of these peaks represents
    # a unique pass. Send that info to the Pass constructor so it can fill in the
    # details.
    passes = []
    evt_ndx = 0
    for evt_time, evt in zip(evt_times, events):
        if evt == 1:    # In Skyfield, an event of 1 is 'culminate' aka peak
            try:
                passes.append(SatellitePass(observer_pos, sat, evt_ndx, evt_time, evt_times, events))
            except ValueError as e:
                # print(e)
                pass
        evt_ndx += 1

    passes.sort()
    return passes
