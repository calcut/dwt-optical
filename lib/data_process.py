import pandas as pd
import numpy as np
import logging
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import re
import Code_17_06_22.GeneralFunctions_17_06_22 as general_functions
import Code_17_06_22.FittingFunctions_17_06_22 as fitting_functions
import Code_17_06_22.FittingSubFunctions_17_06_22 as fitting_subfunctions

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

        self.apply_avg_repeats = True
        self.apply_normalise = True
        self.apply_smooth = True
        self.apply_trim = True
        self.apply_interpolate = True
        self.apply_round = True

        self.calc_fwhm = True
        self.calc_min = True
        self.calc_baseline = False
        self.calc_height = True


    def process_dataframe(self, df):

        if self.apply_avg_repeats:
            df = self.avg_repeats(df)

        if self.apply_trim:
            try:
                df = self.trim(df, self.wavelength_trim_min, self.wavelength_trim_max)
            except:
                logging.exception("Unable to trim")

        if self.apply_smooth:
            try:
                df = self.smooth(df, self.smooth_points)
            except:
                logging.exception("Unable to smooth")

        if self.apply_interpolate:
            try:
                df = self.interpolate(df, self.interpolate_sampling_rate)
            except:
                logging.exception("Unable to interpolate")

        if self.apply_normalise:
            try:
                df = self.normalise(df)
            except:
                logging.exception("Unable to normalise")

        if self.apply_round:
            try:
                df = df.round(self.round_decimals)            
            except:
                logging.exception("Unable to round")

        return df

    def avg_repeats(self, df):

        # Remove any "repXX" from the column names
        # This leaves a dataframe where repeats have identical column names
        regex = re.compile("rep(.*)")
        for col in df.columns[1:]:
            newname = regex.sub("", col)
            df.rename({col : newname}, axis=1, inplace=True)

        # For the each of the new column names
        # check if there are multiple columns and average if so
        for col in df.columns[1:].unique():
            if type(df[col]) == pd.DataFrame:
                df[f"{col}avg"] = df[col].mean(axis=1)
                df.drop(df[col], axis=1, inplace=True)
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

    def get_stats(self, df, peak_type='Min', round_digits=2):

        # this imports the example code rather than re-implementing it

        stats_df = pd.DataFrame(index=df.columns[1:], dtype='float64')
        WavelengthArray = df['wavelength'].tolist()
        
        for col in df.columns[1:]:

            TransArray = df[col].tolist()

            if (peak_type=="Max"):
                for i in range(len(TransArray)):
                    TransArray[i]=TransArray[i]*(-1)

            fwhm, height, baseline = general_functions.FWHM(WavelengthArray, TransArray)
            smoothed_peak = self._smoothed_peak(WavelengthArray, TransArray)

            if self.calc_min:
                stats_df.at[col, 'Peak'] = round(smoothed_peak, round_digits)

            if self.calc_fwhm:
                stats_df.at[col, 'FWHM'] = round(fwhm, round_digits)

            if self.calc_baseline:
                stats_df.at[col, 'Baseline'] = round(baseline, round_digits)

            if self.calc_height:
                stats_df.at[col, 'Height'] = round(height, round_digits)

        return stats_df

    def _smoothed_peak(self, Wavelength, TransArray):

        # Cut at second differentials of polyfit at either side of lowest first
        [WavelengthCut,TransArrayCut]=fitting_functions.PolynomialBasedCut(Wavelength,TransArray)
        [TransArrayCut,WavelengthCut]=fitting_subfunctions.Reframe(WavelengthCut,TransArrayCut)

        # Fit by extreme smoothing of the minima
        peak=fitting_functions.SmoothAndSelect(WavelengthCut,TransArrayCut)

        return peak