import pandas as pd
import numpy as np
import time
import serial
import serial.tools.list_ports
import thorlabs_apt_protocol as apt
import lib.stellarnet_win.stellarnet_driver3 as sn
import logging

logging.basicConfig(level=logging.DEBUG)

class Stellarnet_Thorlabs_Hardware():
    def __init__(self):

        self.encoder_pos_counts = 20000 #per mm
        self.encoder_vel_counts = 204.8 #per mm/s

        self.setup = None
        self.serial_port = None
        self.port = None

    def scan_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        n =1 
        for port, desc, hwid in sorted(ports):
            logging.info(f"{n}) {port}: {desc} [{hwid}]")
            n+=1
        return ports

    def connect(self, setup, serial_port=None):
        self.serial_port = serial_port
        self.setup = setup
        self.thorlabs_setup()
        self.stellarnet_setup()

    def thorlabs_setup(self):
        if self.serial_port:
            if self.port:
                self.port.close()
            self.port = serial.Serial(self.serial_port, 115200, rtscts=True, timeout=0.1)
            self.port.rts = True
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
            self.port.rts = False
            self.port.write(apt.hw_no_flash_programming(source=1, dest=0x21))
            logging.info(f'thorlabs serial connection on {self.serial_port}')

            logging.info('Requesting update msgs from stage')
            self.apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x21))
            self.apt_cmd(apt.hw_start_updatemsgs(source=1, dest=0x22))

            logging.info('Homing stage')
            self.apt_cmd(apt.mot_move_home(source=1, dest=0x21 ,chan_ident=1))
            self.apt_cmd(apt.mot_move_home(source=1, dest=0x22 ,chan_ident=1))
        else:
            self.port=None
            logging.warning('thorlabs serial port not specified')

    def stellarnet_setup(self):
        try:
            self.spectrometer, self.wav = sn.array_get_spec(0) #0 is first channel/spectrometer
            scans_to_avg = self.setup['input_config']['scans_to_avg']
            int_time = self.setup['input_config']['integration_time']
            x_smooth = self.setup['input_config']['x_smooth']
            x_timing = self.setup['input_config']['x_timing']

            self.spectrometer['device'].set_config(int_time=int_time,
                                        scans_to_avg=scans_to_avg,
                                        x_smooth=x_smooth,
                                        x_timing=x_timing)
            logging.info(f'Spectrometer Connected')
            logging.info(f'{scans_to_avg=} {int_time=} {x_smooth=} {x_timing=}')
        except Exception as e:
            logging.warning(f'Stellarnet connection error: {e}')
            self.spectrometer = None

    def apt_cmd(self, cmd_string):
        logging.info(f'{cmd_string.hex()=}')
        if self.port:
            self.port.write(cmd_string)



    def measure(self, setup, row):
        # try:
        element = row['element']
        x_pos = setup['sensor']['layout']['map'][element][0]
        y_pos = setup['sensor']['layout']['map'][element][1]
        wl_min = setup['input_config']['wavelength_range'][0]
        wl_max = setup['input_config']['wavelength_range'][1]

        logging.info(f"\n\nMeasuring Element {element}")
        logging.info(f'{x_pos=} {y_pos=}')
        logging.info(f'{wl_min=} {wl_max=}')


        x_counts = int(x_pos * self.encoder_pos_counts)
        y_counts = int(y_pos * self.encoder_pos_counts)
        self.apt_cmd(apt.mot_move_absolute(source=1, dest=0x21, chan_ident=1, position=x_counts))
        self.apt_cmd(apt.mot_move_absolute(source=1, dest=0x22, chan_ident=1, position=y_counts))
        
        logging.info('waiting for stage to move')
        time.sleep(8)
        # TODO add feedback here so we know when it is ready!!

        
        if self.spectrometer:
            logging.info('capturing spectrum now')
            spectrum = sn.array_spectrum(self.spectrometer, self.wav)

        else:
            logging.info('generating dummy spectrum')
            dummywavelength = list(np.arange(wl_min, wl_max,
            setup['input_config']['wavelength_range'][2])) #step
            size = len(dummywavelength)
            dummydata = list(np.random.random_sample(size))
            spectrum = {'wavelength' : dummywavelength, 'transmission' : dummydata}
            

        df = pd.DataFrame(spectrum, dtype=np.float32)
        df.columns = ['wavelength', 'transmission']
        if wl_min:
            df.drop(df[df['wavelength'] < wl_min].index, inplace=True)

        if wl_max:
            df.drop(df[df['wavelength'] > wl_max].index, inplace=True)

        return df