# dwt-optical
Glasgow University Research Project - Optical Tongue

## Running the GUI

- Complete the installation steps below
- Run the `GUI_main.py` file
   - either from the command line
   - or from within an IDE (e.g [VS Code](https://code.visualstudio.com/))

### Troubleshooting
   - Spectrometer not detected
      - The Libusb "Filter Wizard" tool may need to be re-run
   - Stage not detected / responding
      - try powering the stage controller off and on


## Installation

### Thorlabs Stage
- Download and install Thorlabs [APT Software](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=Motion_Control&viewtab=1)
    - 64 Bit version typically
    - This software itself isn't needed, but it includes the right driver to enable the "Virtual COM Port" option.
    - Note the driver that comes with the alternative "Kinesis" software doesn't support VCP.
- Enable Virtual COM Port
    - Connect and power on the Thorlabs Stage
    - Within Device Manager, find the APT Device > right-click  > Properties > Advanced
    - Enable the VCP checkbox
    - Unplug and reinsert the USB cable
    - A new COM should appear in device manager under Ports

### Stellarnet Spectrometer
- Install the Stellarnet USB Driver
    - Available in this repo [lib/stellarnet_win/SWDriver64.exe](./lib/stellarnet_win/SWDriver64.exe) 
    - Also on Stellarnet USB Stick
    - Right click > Run as Administrator

- A new file will be created at:
    - C:\SWDriver64\Install-SWDriver64.bat
    - Right click > Run as Administrator also

- SpectraWiz software is not needed, but optional



### Python
   - Code has been tested with Python 3.10.6
   - Install python by your preferred means
   - Most straightforward is to install directly from [python.org](https://www.python.org/downloads/)
      - Be sure to check the "Add to Path" box during installation
      - Alternatively use an environment manager like conda or pyenv

### Python Packages
   - Python dependancies need to be installed using pip
   - Open a command prompt and cd to the location of the repo
   e.g `cd C:\Users\calum\git\dwt-optical`
   - Install the packages listed in requirements.txt
      `pip install -r requirements.txt`
   - if the `pip` command isn't recognised, you may have forgotten to add python to path. 
 




