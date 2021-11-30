import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

def resample_df(df, resample):

    wl_min = df['wavelength'].min()
    wl_max = df['wavelength'].max()

    wavel_new = np.arange(wl_min, wl_max, resample)
    result = {}
    for col in df:
        if col == 'wavelength':
            result[col] = wavel_new
        else:
            intfunc = interp1d(df['wavelength'], df[col],
                            'linear', fill_value='extrapolate')
            result[col] = intfunc(wavel_new)
    return pd.DataFrame(result)

def trim_df(df, wl_min, wl_max):
    df = df.loc[df['wavelength'] >= wl_min]
    df = df.loc[df['wavelength'] <= wl_max]
    return df


def normalise_df(df):
    for col in df:
        if col == 'wavelength':
            pass
        else:
            maxval = df[col].max()
            df[col] = df[col] / maxval
    return df

def plot_df(df):
    for col in df:
        if col == 'wavelength':
           pass
        else:
            plt.plot(df['wavelength'], df[col], label=col)

    plt.legend()
    plt.show()