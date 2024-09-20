#!usr/bin/env python3
'''Read and store the calibration parameters for the Yaesu az/el rotator. This is a very important
script since it provides cal data to scripts that want to make sense of the G-550's input values.
To populate a calibration file, you need to run position_testbed.py and record the values you get
for both extremes of both axes.'''

from io import StringIO 

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
            assert(self.min_count < self.max_count)
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
