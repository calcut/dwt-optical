# -*- coding: utf-8 -*-
"""
Created on Mon May 24 15:00:42 2021

@author: IainC
"""
import numpy as np

import warnings

from .FittingSubFunctions_17_06_22 import FindInflections

# For Fittings Only

def PolynomialBasedCut(Wav,Trans):
    Order=51
    DiffArray=[]
    DiffArray2nd=[]
    with warnings.catch_warnings():
            warnings.simplefilter('ignore', np.RankWarning)
            Polys=np.polyfit(Wav,Trans,Order)
            
    for k in range(len(Wav)):
        DVal=0
        for j in range(Order):
            SubDVal=(Order-j)*Polys[j]*(Wav[k]**(Order-j-1))
            DVal=DVal+SubDVal
        DiffArray.append(DVal)
    for k in range(len(Wav)):
        DVal=0
        for j in range(Order-1):
            SubDVal=((Order-j)*(Order-(j+1)))*Polys[j]*(Wav[k]**(Order-j-2))
            DVal=DVal+SubDVal
        DiffArray2nd.append(DVal)
    [Inflections,InflectionTrans]=FindInflections(DiffArray,Wav,Trans)
    MinimaIFIndex=np.argmin(InflectionTrans)
    Minima=Inflections[MinimaIFIndex]
    [Inflections2nd,InflectionTrans2nd]=FindInflections(DiffArray2nd,Wav,Trans)
    
    LeftCut=[]
    RightCut=[]
    for i in range(len(Inflections2nd)):
        Inf2nd=Inflections2nd[i]
        if Inf2nd<Minima and not LeftCut:
            LeftCut=Inf2nd
        if Inf2nd<Minima and Inf2nd>LeftCut:
            LeftCut=Inf2nd
        if Inf2nd>Minima and not RightCut:
            RightCut=Inf2nd
        if Inf2nd>Minima and Inf2nd<RightCut:
            RightCut=Inf2nd
            
    if LeftCut not in Wav:
        LeftCut=Wav[0]
    if RightCut not in Wav:
        RightCut=Wav[len(Wav)-1]
    LeftCutInd=Wav.index(LeftCut)
    RightCutInd=Wav.index(RightCut)
    Wavelength=Wav[LeftCutInd:RightCutInd]
    TransArray=Trans[LeftCutInd:RightCutInd]

    
    return Wavelength, TransArray

def SmoothAndSelect(Wav,Trans):
    Smoothed=[]
    for i in range(15,len(Trans)-15):
        Sum=0
        for j in range(i-15,i+15):
            Sum=Sum+Trans[j]
        Smoothed.append(Sum/30)


    WavTemp=Wav[15:len(Wav)-15]

    if not Smoothed:
        Minima=0
    else:
        Minima=WavTemp[np.argmin(Smoothed)]
    
    return Minima
            
            
        
        