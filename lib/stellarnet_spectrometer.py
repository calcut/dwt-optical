import numpy as np
import pandas as pd
import platform
import logging

logging.basicConfig(level=logging.INFO)
os = platform.system()
if os == 'Windows':
    import stellarnet_win.stellarnet_driver3 as sn
    logging.info('Using Stellarnet Windows driver')
elif os == 'Darwin':
    import stellarnet_mac.stellarnet_driver3 as sn
    logging.info('Using Stellarnet Mac driver')
elif os == 'Linux' and platform.machine() == 'armv7l':
    import stellarnet_rpi.stellarnet_driver3 as sn
    logging.info('Using Stellarnet RaspberryPi driver')
else:
    raise Exception('OS not recognised')

class Stellarnet_Spectrometer():

    def __init__(self):
        self.scans_to_avg = 3
        self.int_time = 450
        self.x_smooth = 1
        self.x_timing = 3
        self.wl_round = 2 #decimal places
        self.wl_min = None #optional wavelength trimming
        self.wl_max = None

        self.light_reference = None
        self.dark_reference = None
        self.spectrometer = None
        logging.info(f'scans_to_avg={self.scans_to_avg} '+
                f'int_time={self.int_time} '+
                f'x_smooth={self.x_smooth} '+
                f'x_timing {self.x_timing}')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def connect(self):
        try:
            self.spectrometer, self.wav = sn.array_get_spec(0) #0 is first channel/spectrometer
            self.spectrometer['device'].set_config(int_time=self.int_time,
                                        scans_to_avg=self.scans_to_avg,
                                        x_smooth=self.x_smooth,
                                        x_timing=self.x_timing)
            logging.info(f'Spectrometer Connected')
            logging.info(f'scans_to_avg={self.scans_to_avg} '+
                         f'int_time={self.int_time} '+
                         f'x_smooth={self.x_smooth} '+
                         f'x_timing={self.x_timing}')
        except Exception as e:
            logging.warning(f'Stellarnet connection error: {e}')
            self.spectrometer = None

    def get_spectrum(self, as_percentage=True, dummy_low=1000, dummy_high=10000):
        if self.spectrometer:
            logging.info('capturing spectrum now')
            spectrum = sn.array_spectrum(self.spectrometer, self.wav)
        else:
            logging.info('generating dummy spectrum')
            dummywavelength = list(np.arange(self.wl_min, self.wl_max, 0.5)) #start stop step
            rng = np.random.default_rng()
            dummydata = rng.integers(dummy_low, dummy_high, size=len(dummywavelength))
            spectrum = {'wavelength' : dummywavelength, 'transmission' : dummydata}

        df = pd.DataFrame(spectrum, dtype=np.float32)
        df.columns = ['wavelength', 'transmission']

        if self.wl_min:
            df.drop(df[df['wavelength'] < self.wl_min].index, inplace=True)

        if self.wl_max:
            df.drop(df[df['wavelength'] > self.wl_max].index, inplace=True)

        if self.wl_round:
            df['wavelength'] = df['wavelength'].round(self.wl_round)

        if as_percentage:
            df = self._calculate_percentage(df)

        return df
        
    def _calculate_percentage(self, df):
        
        if self.light_reference is None:
            logging.error('Light reference spectrum has not been captured')
        if self.dark_reference is None:
            logging.error('Dark reference spectrum has not been captured')

        data = df['transmission']
        dr = self.dark_reference['transmission']
        lr = self.light_reference['transmission']

        if len(data) != len(dr):
            raise Exception('spectrum length does not match dark reference')
        if len(data) != len(lr):
            raise Exception('spectrum length does not match light reference')

        df['transmission'] = (data - dr) / (lr - dr) * 100
        return df

    def capture_dark_reference(self, dummy_val=1000):
        self.dark_reference = self.get_spectrum(as_percentage=False, dummy_low=dummy_val, dummy_high=dummy_val+1)
        # TODO, some code to warn if dark reference looks wrong?

    def capture_light_reference(self, dummy_val=11000):
        self.light_reference = self.get_spectrum(as_percentage=False, dummy_low=dummy_val, dummy_high=dummy_val+1)
        # TODO, some code to warn if light reference looks wrong?


if __name__ == "__main__":

    # Can use with a context manager (with statement) to ensure serial port gets closed.
    with Stellarnet_Spectrometer() as sp:
        sp.connect()
        sp.scans_to_avg = 3
        sp.int_time = 450
        sp.x_smooth = 1
        sp.x_timing = 3
        sp.wl_min = 400
        sp.wl_max = 420
        sp.capture_dark_reference()
        sp.capture_light_reference()

        print(sp.get_spectrum(dummy_low=5000, dummy_high=7000))