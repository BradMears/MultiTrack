#!usr/bin/env python3
'''Read and store the calibration parameters for the Yaesu az/el rotator. This is a very important
script since it provides cal data to scripts that want to make sense of the G-5500's input values.
To populate a calibration file, you need to run position_testbed.py and record the values you get
for both extremes of both axes.'''

from io import StringIO 
from math import isclose

class CalibrationData:
    '''Holds cal data for the azimuth and elevation outputs from the control unit.'''    

    #  Nested class to make it clear that this is part of the CalibrationData
    class AxisData:
        '''Holds cal data for one axis' output from the control unit.'''    
        def __init__(self, line : str):
            #Axis, MinAngle, MinCount, MinVoltage, MaxAngle, MaxCount, MaxVoltage
            fields = line.split(',')
            if len(fields) != 7:
                msg = f'Wrong number of fields. Should be 7\n{line}'
                raise ValueError(msg)
            self.axis = fields[0]
            self.min_angle = float(fields[1])
            self.min_count = int(fields[2])
            self.min_voltage = float(fields[3])
            self.max_angle = float(fields[4])
            self.max_count = int(fields[5])
            self.max_voltage = float(fields[6])
            assert(self.min_angle < self.max_angle)
            assert(self.min_count <= self.max_count)
            assert(self.min_voltage < self.max_voltage)

        def __str__(self):
            return f'{self.min_angle} {self.min_count} {self.min_voltage} {self.max_angle} {self.max_count} {self.max_voltage}'

    # Resume outer class

    def __init__(self, readable):
        '''Constructor will read cal data from a file or a string. Don't invoke this directly. Instead,
        you should use the from_file() or from_string() methods.''' 
        linenum = 0
        for line in readable:
            linenum += 1
            line = line.strip()
            if line.startswith('Az'):
                self.az = self.AxisData(line)
            elif line.startswith('El'):
                self.el = self.AxisData(line)
            elif line.startswith('#'):
                continue
            elif line == '':
                continue
            else:
                msg = f'Unrecognized contents in calibration file on line {linenum}\n{line}'
                raise ValueError(msg)
            
        assert(self.az.axis == 'Az')  # belt and suspenders check that we processed the file correctly
        assert(self.el.axis == 'El')
        

    @classmethod
    def from_file(cls, filename : str ):
        cal_file = open(filename, "r")
        return cls(cal_file)

    @classmethod
    def from_string(cls, raw_string : str ):
        readable = StringIO(raw_string)
        return cls(readable)

    def __str__(self):
        return f'Az cal = {self.az}\nEl cal = {self.el}'

class YaesuG5500Positions:
    '''Utilities to process the raw sensor data from the az/el controller. Does not do any
    device I/O. Just provides ways to make sense of the data once you have it.'''

    def __init__(self, **kwargs):
        '''There are two possible arguments - a filename or a raw string that has the same contents
        as would be found in a cal file.'''
        raw_string = kwargs.get('raw_string')
        filename = kwargs.get('filename', 'rotator_cal.txt')

        if raw_string != None:
            self.cal_data = CalibrationData.from_string(raw_string)
        else:
            assert(raw_string == None)
            self.cal_data = CalibrationData.from_file(filename)

    def voltage_to_degrees(self, az_voltage : float, el_voltage : float):
        '''Computes the current angles in az & el given the voltage of each.'''
        az_deg = (az_voltage - self.cal_data.az.min_voltage) * (self.cal_data.az.max_angle - self.cal_data.az.min_angle) / (self.cal_data.az.max_voltage - self.cal_data.az.min_voltage) 
        el_deg = (el_voltage - self.cal_data.el.min_voltage) * (self.cal_data.el.max_angle - self.cal_data.el.min_angle) / (self.cal_data.el.max_voltage - self.cal_data.el.min_voltage) 
        return az_deg, el_deg

    def count_to_degrees(self, az_count : int, el_count : int):
        '''Computes the current angles in az & el given the count of each.'''
        az_deg = (az_count - self.cal_data.az.min_count) * (self.cal_data.az.max_angle - self.cal_data.az.min_angle) / (self.cal_data.az.max_count - self.cal_data.az.min_count) 
        el_deg = (el_count - self.cal_data.el.min_count) * (self.cal_data.el.max_angle - self.cal_data.el.min_angle) / (self.cal_data.el.max_count - self.cal_data.el.min_count) 
        return az_deg, el_deg
    
    def __str__(self):
        return str(self.cal_data)

class G5500:
    '''
    Abstract interface for controlling a Yaesu G5500 rotator. This class does not do any device I/O.
    It just defines the interface and base functionality. Subclasses must implement the required
    device I/O routines.
    '''

    def __init__(self, cal_file : str):
        '''Constructor.'''
        self.rotator = YaesuG5500Positions(filename=cal_file)
        self.az = None  # Current azimuth position in degrees
        self.el = None  # Current elevation position in degrees
        self.pwr_on = False  # Power-on state of the rotator

    def stop_motion(self):
        '''Stops all motion of the rotator.'''
        raise NotImplementedError('stop_motion() must be implemented in a subclass')
    
    def move_az_right(self):
        '''Starts motion to increase azimuth.'''
        raise NotImplementedError('move_az_right() must be implemented in a subclass')
    
    def move_az_left(self):
        '''Starts motion to decrease azimuth.'''
        raise NotImplementedError('move_az_left() must be implemented in a subclass')
    
    def move_el_up(self):
        '''Starts motion to increase elevation.'''
        raise NotImplementedError('move_el_up() must be implemented in a subclass')
    
    def move_el_down(self):
        '''Starts motion to decrease elevation.'''
        raise NotImplementedError('move_el_down() must be implemented in a subclass')
    
    def read_sensors(self) -> tuple[float, float, bool]:
        '''Reads the current positions from the rotator and updates self.az and self.el.
        Also reads the power-on state of the rotator.
        Returns a tuple of (az, el, pwr_on) in (degrees, degrees, bool).'''
        raise NotImplementedError('read_sensors() must be implemented in a subclass')
    
    def voltage_to_degrees(self, az_voltage : float, el_voltage : float) -> tuple[float, float]:
        '''Computes the current angles in az & el given the voltage of each.'''
        return self.rotator.voltage_to_degrees(az_voltage, el_voltage)

    def count_to_degrees(self, az_count : int, el_count : int) -> tuple[float, float]:
        '''Computes the current angles in az & el given the count of each.'''
        return self.rotator.count_to_degrees(az_count, el_count)

    def __str__(self):
        return f'Power ON = {self.pwr_on}\tAz = {self.az}\tEl = {self.el}'



# Unit tests - run with pytest
import pytest

class TestYaesuG5500Positions: 
    @pytest.fixture(autouse=True) 
    def _setup(self): 
        test_str = '''# Calibration test data
                    # Axis, MinAngle, MinCount, MinVoltage, MaxAngle, MaxCount, MaxVoltage
                    #  
                    Az, 0, 0, 0, 540, 32000, 4.0
                    El, 0, 0, 0, 180.0, 32000, 4.0
                    '''
        self.rotator = YaesuG5500Positions(raw_string=test_str)
        
    def test_voltage_to_degrees(self):
        '''Tests that we didn't mess up the very simple math in the conversion.'''
        assert(self.rotator.voltage_to_degrees(0, 0) == (0,0))
        assert(self.rotator.voltage_to_degrees(2, 2) == (270, 90))
        assert(self.rotator.voltage_to_degrees(4, 4) == (540, 180))
        assert(self.rotator.voltage_to_degrees(3, 1) == (405, 45))

    def test_counts_to_degrees(self):
        '''Tests that we didn't mess up the very simple math in the conversion.'''
        assert(self.rotator.count_to_degrees(0, 0) == (0,0))
        assert(self.rotator.count_to_degrees(16000, 16000) == (270, 90))
        assert(self.rotator.count_to_degrees(32000, 32000) == (540, 180))
        assert(self.rotator.count_to_degrees(10000, 20000) == (168.75, 112.5))

    def test_actual_problem(self):
        '''Tests a problem I ran into with live data. I was getting bad positions
        from voltage_to_degrees and count_to_degrees using fresh cal data.'''
        # Since the low end of az range matches the actual az data, why don't the calculated 
        # positions come out to zero?
        # Actual data from the actual device given the cal data shown below
        # Az =    3.54°    3.54° (   0.00°)   208   0.026V        El =    1.64°    1.73° (  -0.09°)   304   0.036V

        actual_cal_data = '''
            # Calibration captured 2024-09-15
            Az, 0, 208, 0.026, 540, 31920, 3.988
            El, 0, 288, 0.038, 180, 31984, 3.998
            '''
        rotator = YaesuG5500Positions(raw_string=actual_cal_data)

        # Test ideal values that should match the extremes of the range
        assert(rotator.count_to_degrees(208, 288) == (0,0))
        assert(rotator.voltage_to_degrees(3.988, 3.998) == (540, 180))


        # Test actual values we got from the device
        #assert(rotator.count_to_degrees(208, 304) == (0,0))
        #assert(rotator.voltage_to_degrees(0.026, 0.036) == (0,0))

    def test_labjack_problem(self):
        '''Tests another real problem I ran into where the calculated azimuth position 
        did not match the position reported on the dial.'''
        # Calibration captured 2024-09-21
        actual_cal_data = '''
            # Calibration captured 2024-09-21
            Az, 0, 0, 0.034538, 450, 0, 4.006422
            El, 0, 0, 0.043038, 180, 0, 4.008255
            '''
    
        # 1/2 a degree sounds like a lot and I guess it is but the sensors on the rotator
        # are not perfect.
        #ABS_TOL_DEG = 0.5

        # 2% also sounds like a lot.
        REL_TOL_DEG = 0.02

        #Az =  112.79°    0.86V  El =    0.00°   0.043V
        # Indicated Az was 90 degrees not 112
        # The problem was fixed when I realized a entered 540 in the cal file raher than 450.
        # Still, I'll keep the unit test since I have it
        rotator = YaesuG5500Positions(raw_string=actual_cal_data)
        az,el = rotator.voltage_to_degrees(0.82, 3.998)
        assert(isclose(az, 90, rel_tol=REL_TOL_DEG))
        assert(isclose(el, 180, rel_tol=REL_TOL_DEG))
