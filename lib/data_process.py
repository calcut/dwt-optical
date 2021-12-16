import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

def Interpolate(df, SamplingRate):

    wl_min = df['wavelength'].min()
    wl_max = df['wavelength'].max()

    wavel_new = np.arange(wl_min, wl_max, SamplingRate)
    result = {}
    for col in df:
        if col == 'wavelength':
            result[col] = wavel_new
        else:
            f= interp1d(df['wavelength'], df[col],
                            'linear', fill_value='linear')
            result[col] = f(wavel_new)
    return pd.DataFrame(result)

def trim(df, wl_min, wl_max):
    df = df.loc[df['wavelength'] >= wl_min]
    df = df.loc[df['wavelength'] <= wl_max]
    return df


def normalise(df):
    for col in df:
        if col == 'wavelength':
            pass
        else:
            maxval = df[col].max()
            df[col] = df[col] / maxval
    return df

def smooth(df, SmoothPoints=3):
    df = df.rolling(window=SmoothPoints).mean()

def plot(df):
    for col in df:
        if col == 'wavelength':
           pass
        else:
            plt.plot(df['wavelength'], df[col], label=col)

    plt.legend()
    plt.xlabel("Wavelength (nm)", fontsize=20)
    plt.ylabel("Transmission (%)", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    fig=plt.gcf()
    fig.set_size_inches(15, 8)
    # plt.figure().set
    # FigTemp.set_size_inches(15, 8)
    # plt.legend(LegendArray,fontsize=15)
    # plt.title(Sensor[0:(len(Sensor)-1)],fontsize=25, fontweight="bold")
    plt.show()