'''Reads an MCP9808 temperature sensor via I2C and prints the temp.'''

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import adafruit_mcp9808 

# Create sensor object, using the board's default I2C bus.
i2c = busio.I2C(board.SCL, board.SDA)
mcp9808 = adafruit_mcp9808.MCP9808(i2c)

while True:
    print("\nTemperature: %0.1f C" % mcp9808.temperature)
    time.sleep(2)
