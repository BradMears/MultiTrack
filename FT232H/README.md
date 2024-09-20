# Sample scripts to work with the FT232H board

These scripts use CircuitPython libraries from Adafruit as well as a lower-level library called pyftdi. 
These libraries are installed in a python venv named ftdi_venv. Note that to make the Adafruit libraries 
work, you must set an environment variable before calling python scripts that use them.

    export BLINKA_FT232H=1

Adafruit's examples are at https://learn.adafruit.com/circuitpython-on-any-computer-with-ft232h/gpio

The pinout diagram of the FT232H is at https://learn.adafruit.com/assets/88862

## Creating a virtual env 
The required libraries were saved to a file in this directory named pip_requirements.txt. If you
need to recreate the venv, just create it in the normal way and then import the libraries using
pip.

python -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
pip install -r pip_requirements.txt

(For reference, the requirements files was saved using 'pip3 freeze > pip_requirements.txt')
