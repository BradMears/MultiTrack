'''Hook the az/el controller to the LabJack's ADC pins and ensure we can
read azimuth and elevation positions.'''

from time import sleep
import GS5500
import GS5500_LabJackIF
from labjack import ljm

# Set pin assignments based on whether we are using the DB15 connector or the main body terminals
USING_DB15 = False  # Set to True if using DB15 connector, False for main body terminals
#USING_DB15 = True # Uncomment this line to use the DB15 connector
INPUT_PORTS, OUPUT_PORTS = GS5500_LabJackIF.use_db15() if USING_DB15 else GS5500_LabJackIF.use_main_body()

rotator = GS5500.YaesuG5500Positions()  # This will only work if the cal file is up to date

def read_inputs():
    names = [INPUT_PORTS['az_in'], INPUT_PORTS['el_in'], INPUT_PORTS['pwr_on_in']]
    numFrames = len(names)
    while True:
        # Setup and call eReadNames to read values from the LabJack.
        az_v, el_v, pwr_on_v = ljm.eReadNames(handle, numFrames, names)
        print(f'Power signal = {pwr_on_v:7.2f}V\t',end='')
        
        # Axis, MinAngle, MinCount, MinVoltage, MaxAngle, MaxCount, MaxVoltage
        az_deg_v, el_deg_v = rotator.voltage_to_degrees(az_v, el_v)
        az_diff = az_deg_v - az_deg_v
        print(f'Az = {az_deg_v:7.2f}{D} {az_v:7.2}V\t',end='')
        print(f'El = {el_deg_v:7.2f}{D} {el_v:7.2}V')


if __name__ == "__main__":
    # Open the first found LabJack T4. I only have one so conflicts aren't likely.
    # If you have more than one, you may need to specify the serial number or IP
    # address of the LabJack T4 you want to use.
    handle = ljm.openS("T4", "ANY", "ANY")  # Any T4, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    # Keeping the name short to prevent the print statements from getting too long
    D = u'\N{DEGREE SIGN}'

    try:
        names = [INPUT_PORTS['az_in'], INPUT_PORTS['el_in']]
        numFrames = len(names)
        while True:
            # Setup and call eReadNames to read values from the LabJack.
            az_v, el_v = ljm.eReadNames(handle, numFrames, names)

            # Axis, MinAngle, MinCount, MinVoltage, MaxAngle, MaxCount, MaxVoltage
            az_deg_v, el_deg_v = rotator.voltage_to_degrees(az_v, el_v)
            az_diff = az_deg_v - az_deg_v
            print(f'Az = {az_deg_v:7.2f}{D} {az_v:7.2}V\t',end='')
            print(f'El = {el_deg_v:7.2f}{D} {el_v:7.2}V')

            sleep(2)
    except KeyboardInterrupt:
        print("Bye")

    # Close handle
    ljm.close(handle)     
