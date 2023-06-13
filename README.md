# dwt-optical
Glasgow University Research Project - Optical Tongue

## Running the GUI
- Complete the Driver Installation steps below
- Download and run the latest GUI_main.exe file available on the [releases page](https://github.com/calcut/dwt-optical/releases)
   - Alternatively, the GUI_main.py file can be run from a python environment, see Python Installation below.

### Troubleshooting
   - Spectrometer not detected
      - The Libusb "Filter Wizard" tool may need to be re-run
   - Stage not detected / responding
      - try powering the stage controller off and on
   - GUI hangs or has unexpected behaviour
      - This could be caused by e.g. removing or editing data, setup or index files manually while it is open
      - Close and reopen the GUI



## Driver Installation

The software will run without these, but will fail to communicate with the hardware.
e.g. Thorlabs drivers are optional if only using the Stellarnet spectrophotometer.

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

### Stellarnet Driver
- Install the Stellarnet USB Driver
    - Available in this repo [lib/stellarnet_win/SWDriver64.exe](./lib/stellarnet_win/SWDriver64.exe) 
    - Also on Stellarnet USB Stick
    - Right click > Run as Administrator

- A new file will be created at:
    - C:\SWDriver64\Install-SWDriver64.bat
    - Right click > Run as Administrator also

- SpectraWiz software is not needed, but optional

### Libusb Filter 
   - This is required so python can communicate with the spectrometer
      - Install from this repo
      - [lib/stellarnet_win/libusb-win32-devel-filter-1.2.6.0.exe](./lib/stellarnet_win/libusb-win32-devel-filter-1.2.6.0.exe)
   - Run the Filter Wizard tool to install a filter
   - Select the Stellarnet Spectrometer from the list of devices
      - NB **This step will need repeated** if the hardware setup changes 


## Python Installation

These steps are not required if running from the .exe file

### Python
   - Code has been tested with Python 3.10.6
   - Install python by your preferred means
   - Most straightforward is to install directly from [python.org](https://www.python.org/downloads/)
      - Be sure to **check the "Add to Path"** box during installation
      - Alternatively use an environment manager like conda or pyenv

### Python Packages
   - Python dependancies need to be installed using pip
   - Open a command prompt and cd to the location of the repo
   e.g `cd C:\Users\calum\git\dwt-optical`
   - Install the packages listed in requirements.txt
      `pip install -r requirements.txt`
   - if the `pip` command isn't recognised, you may have forgotten to add python to path. 
 




