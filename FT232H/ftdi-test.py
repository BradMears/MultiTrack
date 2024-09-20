#!/usr/bin/env python3

# This script uses pyfdti directly but I never got it to work correctly.
# When it sets a pin low, the voltage goes to 1.9 instead of zero.
# THis script was superceded by the ones that use Adafruit's Blinka library.

from time import sleep
from pyftdi.gpio import GpioAsyncController
print('Hello ftdi')

gpio = GpioAsyncController()
#sps = gpio.configure('ftdi:///1', direction=0x76)
#sps = gpio.configure('ftdi:///1', direction=0xff)
gpio.open_from_url('ftdi:///1', direction=0xff)

# all output set high
gpio.write(0xff)
sleep(2)

# all output set low
gpio.write(0x00)

gpio.close()


'''
# all output set low
gpio.write(0x00)
# all output set high
gpio.write(0x76)
# all output set high, apply direction mask
gpio.write(0xFF & gpio.direction)
# all output forced to high, writing to input pins is illegal
gpio.write(0xFF)  # raises an IOError
gpio.close()
'''
