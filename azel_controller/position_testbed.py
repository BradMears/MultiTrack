'''Test out the ADS1115 hooked up to the az/el controller to ensure we can
read azimuth and elevation positions.'''

from time import sleep
import board
import digitalio 
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import GS5500

rotator = GS5500.YaesuG5500Positions()  # This will only work if the cal file is up to date

MOVE = True
STOP = False

def stop_all_motion():
    az_right.value = STOP
    az_left.value = STOP
    el_up.value = STOP
    el_down.value = STOP

if __name__ == "__main__":
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    az_pos = AnalogIn(ads, ADS.P0)
    el_pos = AnalogIn(ads, ADS.P2)

    az_right = digitalio.DigitalInOut(board.C3)
    az_right.direction = digitalio.Direction.OUTPUT
    az_right.value = STOP

    az_left = digitalio.DigitalInOut(board.C2)
    az_left.direction = digitalio.Direction.OUTPUT
    az_left.value = STOP

    el_up = digitalio.DigitalInOut(board.C1)
    el_up.direction = digitalio.Direction.OUTPUT
    el_up.value = STOP

    el_down = digitalio.DigitalInOut(board.C0)
    el_down.direction = digitalio.Direction.OUTPUT
    el_down.value = STOP
    
    # Keeping the name short to prevent the print statements from getting too long
    D = u'\N{DEGREE SIGN}'

    try:
        while True:
            # Axis, MinAngle, MinCount, MinVoltage, MaxAngle, MaxCount, MaxVoltage
            az_deg_v, el_deg_v = rotator.voltage_to_degrees(az_pos.voltage, el_pos.voltage)
            az_diff = az_deg_v - az_deg_v
            az_deg_c, el_deg_c = rotator.count_to_degrees(az_pos.value, el_pos.value)
            el_diff = el_deg_v - el_deg_c
            print(f'Az = {az_deg_v:7.2f}{D} {az_deg_c:7.2f}{D} ({az_diff:7.2f}{D}) {az_pos.value:5} {az_pos.voltage:7.2}V\t',end='')
            print(f'El = {el_deg_v:7.2f}{D} {el_deg_c:7.2f}{D} ({el_diff:7.2f}{D}) {el_pos.value:5} {el_pos.voltage:7.2}V')

            #az_deg, el_deg = rotator.count_to_degrees(az_pos.value, el_pos.value)
            #print(f'Az = {az_deg:7.2f} {az_pos.value:5}  {az_pos.voltage:5.2f}\t',end='')
            #print(f'El = {el_deg:7.2f} {el_pos.value:5}  {el_pos.voltage:5.2f}')
            sleep(1)
    except KeyboardInterrupt:
        stop_all_motion()
        print("Bye")
        