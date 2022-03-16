import pandas as pd
import numpy as np
import logging
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

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


class DataProcessor():
    '''
    A class to combine all the processing functions into one unit, while
    storing the parameters
    '''
    def __init__(self):

        # Some defaults
        self.smooth_points=3
        self.wavelength_trim_min = 540
        self.wavelength_trim_max = 730
        self.round_decimals = 3
        self.interpolate_sampling_rate = 1.0

        self.apply_normalise = True
        self.apply_smooth = True
        self.apply_trim = True
        self.apply_interpolate = True
        self.apply_round = True

    def process_dataframe(self, df):
        if self.apply_smooth:
            df = self.smooth(df, self.smooth_points)
        
        if self.apply_trim:
            df = self.trim(df, self.wavelength_trim_min, self.wavelength_trim_max)

        if self.apply_normalise:
            df = self.normalise(df)

        if self.apply_interpolate:
            df = self.interpolate(df, self.interpolate_sampling_rate)

        if self.apply_round:
            df = df.round(self.round_decimals)

        return df

    def interpolate(self, df, SamplingRate):

        wl_min = df['wavelength'].min()
        wl_max = df['wavelength'].max()

        wavel_new = np.arange(wl_min, wl_max, SamplingRate)
        result = {}
        for col in df:
            if col == 'wavelength':
                result[col] = wavel_new
            else:
                try:
                    f= interp1d(df['wavelength'], df[col],
                                    'linear', fill_value='linear')
                    result[col] = f(wavel_new)
                except ValueError as e:
                    logging.error(e+"\nThis may be because multiple columns have identical names")

        return pd.DataFrame(result)

    def trim(self, df, wl_min, wl_max):
        df = df.loc[df['wavelength'] >= wl_min]
        df = df.loc[df['wavelength'] <= wl_max]
        return df


    def normalise(self, df):
        for col in df:
            if col == 'wavelength':
                pass
            else:
                maxval = df[col].max()
                df[col] = df[col] / maxval
        return df

    def smooth(self, df, smooth_points=3):
        df = df.rolling(window=smooth_points).mean()
        return df

