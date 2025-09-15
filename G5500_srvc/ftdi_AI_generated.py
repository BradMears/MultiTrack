# You may need to install pyftdi first:
# pip install pyftdi

import time
from pyftdi.gpio import GpioController

# Change this URL to match your FTDI device
FTDI_URL = 'ftdi://ftdi:232h/1'

def main():
    gpio = GpioController()
    # Configure D0 as output (bitmask 0x01)
    gpio.configure(FTDI_URL, direction=0x01)
    try:
        while True:
            # Turn LED on (set D0 high)
            gpio.write(0x01)
            time.sleep(1)
            # Turn LED off (set D0 low)
            gpio.write(0x00)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        gpio.close()

if __name__ == '__main__':
    main()


exit()

from pyftdi.gpio import GpioController
import time

# FTDI URL: adapt to your device (see pyftdi documentation)
ftdi_url = 'ftdi://ftdi:232h/1'

# Pin C5 is bit 5 on port C (bits 16-23), so mask is 1 << (16 + 5) = 1 << 21
C5_MASK = 1 << 21

gpio = GpioController()
gpio.configure(ftdi_url, direction=C5_MASK)

try:
    while True:
        gpio.write(C5_MASK)  # LED ON
        time.sleep(1)
        gpio.write(0)        # LED OFF
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    gpio.close()    
    