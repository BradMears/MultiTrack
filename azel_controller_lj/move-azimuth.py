'''Testing the az/el controller. Very first attempt to write to the FT232H and the G-5500.'''

from time import sleep
import board
import digitalio

MOVE = True
STOP = False

azLeft = digitalio.DigitalInOut(board.C0)
azLeft.direction = digitalio.Direction.OUTPUT
azLeft.value = STOP
sleep(3)

print('Moving left')
azLeft.value = MOVE
sleep(3)
azLeft.value = STOP
print('Stopped moving')
sleep(3)
