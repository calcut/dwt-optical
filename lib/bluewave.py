import numpy as np
import pandas as pd
import stellarnet_mac.stellarnet_driver3 as sn

def get_spectrum(wl_min=None, wl_max=None, int_time=100, scans_to_avg=1, x_smooth=1, x_timing=3):

    try:
        spectrometer, wav = sn.array_get_spec(0) #0 is first channel/spectrometer
        id = spectrometer['device'].get_device_id()
        coeffs_info = spectrometer['device'].get_config()['coeffs']
        print(f'{id=}')
        print(f'{coeffs_info=}')
        spectrometer['device'].set_config(int_time=int_time,
                                        scans_to_avg=scans_to_avg,
                                        x_smooth=x_smooth,
                                        x_timing=x_timing)
        spectrum = sn.array_spectrum(spectrometer, wav)
        df = pd.DataFrame(spectrum, dtype=np.float32)
        df.columns = ['wavelength', 'transmission']

        print(f"{df[df['wavelength'] < 500].index=}")

        if wl_min:
            df.drop(df[df['wavelength'] < wl_min].index, inplace=True)

        if wl_max:
            df.drop(df[df['wavelength'] > wl_max].index, inplace=True)

        print(df)
    except Exception as e:
        print(e)
    
if __name__ == "__main__":
    # just an example
    get_spectrum(wl_min=350, wl_max=1000)

