'''Hook the FT232H to the ADS1115 via I2C and print the values reported
by the ADC. This allows me to feed the ADC from the bench power supply 
and figure out its limits.'''

from time import sleep
import board
import digitalio 
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


if __name__ == "__main__":
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    p0 = AnalogIn(ads, ADS.P0)
    p1 = AnalogIn(ads, ADS.P1)
    p2 = AnalogIn(ads, ADS.P2)
    p3 = AnalogIn(ads, ADS.P3)

    
    try:
        while True:
            print(f'({p0.value:5} {p0.voltage:5.3}) ', end='')
            print(f'({p1.value:5} {p1.voltage:5.3}) ', end='')
            print(f'({p2.value:5} {p2.voltage:5.3}) ', end='')
            print(f'({p3.value:5} {p3.voltage:5.3}) ')
            sleep(2)
    except KeyboardInterrupt:
        print("Bye")