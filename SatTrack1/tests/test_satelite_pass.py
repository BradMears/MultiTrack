'''pytest for the SatellitePass class.'''

import pytest
import pytz
import json
from SatellitePass import SatellitePass, upcoming_passes
from skyfield.api import load
from skyfield.api import wgs84
from skyfield.timelib import Time
from skyfield.api import EarthSatellite

# Uses a JSON file from a saved date so the results won't change as new orbital
# elements are released.

def set_globals():
    '''This is almost certainly an anti-pattern but I haven't seen a better way
    to do one-time initialization of a handful of objects in pytest. I'm sure 
    I'll find a better way and look at this aghast that I did it this way.'''

    # Set the observer coordinates and timezone 
    lat = 38.9596
    lon = -104.7695
    elev = 2092

    SatellitePass.TZ = pytz.timezone("America/Denver")
    
    # Get the fake time in skyfield format and in regular python datetime
    ts = load.timescale()

    with load.open('amateur-241102.json') as f:
        amsats_json = json.load(f)

    # Anything the test cases want to use are stored in pytest
    pytest.amsats = [EarthSatellite.from_omm(ts, fields) for fields in amsats_json]
    pytest.t = Time(tt=2460617.3960255613, ts=ts)  # Time is stuck at 3:29 PM on Nov 2, 2024
    pytest.t_end = pytest.t + 4 / 24
    pytest.obs_pos = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m = elev)

set_globals()

@pytest.mark.parametrize("satnum, passes, fails", 
                         [(14781, 1, 0), 
                          (60240, 1, 0), 
                          (23439, 0, 1), 
                          (53106, 0, 1),
                          (44854, 0, 0) ])
def test_passes_and_fails(satnum, passes, fails):
    sat = next((x for x in pytest.amsats if x.model.satnum == satnum), None)
    # Find all upcoming passes over 30 degrees in the desired timeframe
    sat_passes, failed_passes = upcoming_passes(pytest.obs_pos, sat, 30.0, pytest.t, pytest.t_end)
    assert len(sat_passes) == passes
    assert len(failed_passes) == fails

# This is a pretty sparse test suite. It could use some more test cases to
# exercise SatellitePass directly and not just upcoming_passes(). 

