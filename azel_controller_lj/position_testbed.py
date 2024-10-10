'''Hook the az/el controller to the LabJack's ADC pins and ensure we can
read azimuth and elevation positions.'''

from time import sleep
import GS5500
from labjack import ljm

rotator = GS5500.YaesuG5500Positions()  # This will only work if the cal file is up to date

if __name__ == "__main__":
    # Open first found LabJack
    handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier

    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    deviceType = info[0]

    # Keeping the name short to prevent the print statements from getting too long
    D = u'\N{DEGREE SIGN}'

    try:
        while True:
            # Setup and call eReadNames to read values from the LabJack.
            names = ['AIN0', 'AIN1']
            numFrames = len(names)

            #results = ljm.eReadNames(handle, numFrames, names)
            #print("\neReadNames results: ")
            #for i in range(numFrames):
            #    print("    Name - %s, value : %f" % (names[i], results[i]))

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
