import pandas as pd
import numpy as np
import logging
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import re
# import Code_17_06_22.GeneralFunctions_17_06_22 as general_functions
import Code_17_06_22.FittingFunctions_17_06_22 as fitting_functions
import Code_17_06_22.FittingSubFunctions_17_06_22 as fitting_subfunctions

def plot(df):
    for col in df:
        plt.plot(df.index, df[col], label=col)

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
        self.calc_inflections = True


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
        regex = re.compile("(.*)rep(.*)")
        for col in df.columns:
            newname = regex.search(col).group(1)
            df.rename({col : newname}, axis=1, inplace=True)

        suffix = "_avg"
        if newname == "":
            suffix = "avg"

        # For the each of the new column names
        # check if there are multiple columns and average if so
        for col in df.columns.unique():
            if type(df[col]) == pd.DataFrame:
                df[f"{col}{suffix}"] = df[col].mean(axis=1)
                df.drop(df[col], axis=1, inplace=True)
            else:
                # Rename the column to include _avg, even if only 1 measurement 
                df.rename({col : f"{col}{suffix}"}, axis=1, inplace=True)
        return df

    def interpolate(self, df, SamplingRate):

        wl_min = df.index.min()
        wl_max = df.index.max()

        wavel_new = np.arange(wl_min, wl_max, SamplingRate)
        result = {}
        for col in df:
            try:
                f= interp1d(df.index, df[col],
                                'linear', fill_value='linear')
                result[col] = f(wavel_new)
            except ValueError as e:
                logging.error(e+"\nThis may be because multiple columns have identical names")

        result['wavelength'] = wavel_new

        df_interpolated = pd.DataFrame(result)
        df_interpolated.set_index('wavelength', inplace=True)

        return df_interpolated

    def trim(self, df, wl_min, wl_max):
        df = df.loc[df.index >= wl_min]
        df = df.loc[df.index <= wl_max]
        return df

    def normalise(self, df):
        for col in df:
            maxval = df[col].max()
            minval = df[col].min()
            df[col] = (df[col]-minval) / (maxval - minval)
        return df

    def smooth(self, df, smooth_points=3):
        df = df.rolling(window=smooth_points, center=True).mean()

        # fill any NaN values
        # the rolling mean generates NaN at the start and end, which can trip up other processing
        df.fillna(method='pad', inplace=True)
        df.fillna(method='backfill', inplace=True)

        return df

    def get_stats(self, df, peak_type='Min', round_digits=3, std_deviation=False, peak_algo="quadratic"):

        # this imports the example code rather than re-implementing it
        stats_df = pd.DataFrame(index=df.columns, dtype='float64')
        WavelengthArray = df.index.tolist()
        
        for col in df.columns:

            TransArray = df[col].tolist()

            if (peak_type=="Max"):
                for i in range(len(TransArray)):
                    TransArray[i]=TransArray[i]*(-1)

            # fwhm, height, baseline = general_functions.FWHM(WavelengthArray, TransArray)
            fwhm, height, baseline = self.FWHM(df, col)

            if peak_algo == "poly51":
                smoothed_peak = self._smoothed_peak(WavelengthArray, TransArray)
            elif peak_algo == "quadratic":
                smoothed_peak = self.quadratic_peak(WavelengthArray, TransArray)

            if self.calc_min:
                stats_df.at[col, 'Peak'] = round(smoothed_peak, round_digits)

            if self.calc_fwhm:
                stats_df.at[col, 'FWHM'] = round(fwhm, round_digits)

            if self.calc_baseline:
                stats_df.at[col, 'Baseline'] = round(baseline, round_digits)

            if self.calc_height:
                stats_df.at[col, 'Height'] = round(height, round_digits)

            if self.calc_inflections:
                inflection_min, inflection_max = self._get_inflections(df, col, trim_nm=100, smooth_points=30) 
                stats_df.at[col, 'Infl_L'] = round(inflection_min, round_digits)
                stats_df.at[col, 'Infl_R'] = round(inflection_max, round_digits)

        if std_deviation:

            stats_avg_df = pd.DataFrame(index=['averaged'], dtype='float64')
            for col in stats_df.columns:
                stats_avg_df[f"{col}"] = round(stats_df[col].mean(axis=0), round_digits)
            for col in stats_df.columns:
                stats_avg_df[f"{col}-SD"] = round(stats_df[col].std(axis=0), round_digits)
            return stats_avg_df

        else:
            return stats_df
        
    def quadratic_peak(self, Wavelength, TransArray, bandwidth=20):

        # Use the raw minimum (no smoothing) initially
        min_index = np.argmin(TransArray)

        # Use pandas series to enable logical indexing
        wl = pd.Series(Wavelength)
        trans = pd.Series(TransArray)

        # Get index of data within +/- bandwidth/2 from the minimum
        index = abs(wl - wl[min_index]) < bandwidth/2

        # Get the wavelength and transmission data within the bandwidth
        WavelengthRange = wl[index]
        TransRange = trans[index]

        px = np.polyfit(WavelengthRange,TransRange,2)
        a = px[0]
        b = px[1]

        # outputs are a bit of algebra based on quadratic fit
        QuadraticFitParameter = a
        ResonancePeak = -b/2/a
        ResonancePeaksValue = np.polyval(px, -b/2/a)

        # print(f'{QuadraticFitParameter=} {ResonancePeak=} {ResonancePeaksValue=}')

        return ResonancePeak

    def _smoothed_peak(self, Wavelength, TransArray):

        # Cut at second differentials of polyfit at either side of lowest first
        [WavelengthCut,TransArrayCut]=fitting_functions.PolynomialBasedCut(Wavelength,TransArray)
        [TransArrayCut,WavelengthCut]=fitting_subfunctions.Reframe(WavelengthCut,TransArrayCut)

        # Fit by extreme smoothing of the minima
        peak=fitting_functions.SmoothAndSelect(WavelengthCut,TransArrayCut)

        return peak

    def _get_inflections(self, df, col, trim_nm=100, smooth_points=30):
        
        # Currently processes only a single column
        trans_series = df[col]

        # smooth first
        trans_smoothed = trans_series.rolling(window=smooth_points, center=True).mean()

        # Get the wavelength of the literal minimum
        wl_minimum = trans_smoothed.idxmin()

        # trim at +/- trim_nm around the minimum
        trans_smoothed = trans_smoothed.loc[trans_smoothed.index >= wl_minimum -trim_nm]
        trans_smoothed = trans_smoothed.loc[trans_smoothed.index <= wl_minimum +trim_nm]

        # create a wavelength series so the .diff() function on it
        wl_series = trans_smoothed.index.to_series()

        # This does a simple delta y / delta x type of derivative
        trans_deriv = trans_smoothed.diff() / wl_series.diff()
        
        # Inflections are the wavelengths of the min and max of the derivative
        inflection_min = trans_deriv.idxmin()
        inflection_max = trans_deriv.idxmax()

        return inflection_min, inflection_max 

    def FWHM(self, df, col):

        trans = df[col]
        baseline = trans.iloc[1:101].mean()
        min = trans.iloc[1:].min()
        height = baseline - min
        half_max = min + height/2

        # get wavelengths where the data is <= half max
        hm_range = trans[trans <= half_max].index
        fwhm = hm_range[-1] - hm_range[0]

        return fwhm, height, baseline
