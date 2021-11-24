# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 11:08:52 2021

@author: IainC
"""

# Sia Functions

import numpy as np
from scipy.interpolate import interp1d

def Normalise(Trans):
    Trans1=[]
    MaxVal = np.max(Trans)
    for i in range(len(Trans)):
        normal = Trans[i] / MaxVal
        Trans1.append(normal)
    return Trans1
                                
                        
                        
def Interpolate(Wav,Trans,SamplingRate):
    f = interp1d(Wav, Trans, 'linear')
    WavStart=min(Wav)
    WavEnd=max(Wav)
    WavInterpolated =  np.arange(WavStart, WavEnd, SamplingRate)
    TransInterpolated = f(WavInterpolated) 
    TransInterpolated1=[]
    WavInterpolated1=[]
    for i in range(len(TransInterpolated)):
        TransInterpolated1.append(TransInterpolated[i])
    for i in range(len(WavInterpolated)):
        WavInterpolated1.append(WavInterpolated[i])
    
    return (WavInterpolated1,TransInterpolated1)
                    