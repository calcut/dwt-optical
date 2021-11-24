# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 16:08:53 2020

@author: IainC
"""

# Intake of Spectra depending on spectrometer

from GeneralFunctions_17_11_21 import FWHM
from GeneralFunctions_17_11_21 import CreateBlank
from GeneralFunctions_17_11_21 import WavExtract
from GeneralFunctions_17_11_21 import TransExtract
from GeneralFunctions_17_11_21 import Format

from FittingFunctions_17_11_21 import PolynomialBasedCut
from FittingFunctions_17_11_21 import SmoothAndSelect

from FittingSubFunctions_17_11_21 import Reframe

from SiaFunctions_18_11_21 import Normalise
from SiaFunctions_18_11_21 import Interpolate
import os
import csv

# SpectraWiz
def SpectraWiz(DataSet,SampleNames,Sensors,FileNames,Smooth,SmoothPoints,NormaliseQ,InterpolateQ,SamplingRate):
    
    FigNum=0

    Wavelength=[]
    AverageTransArray=[]
    
    MinimaArray=[0]*len(SampleNames)
    for i in range(len(SampleNames)):
        MinimaArray[i]=[]
        for j in range(len(Sensors)):
            MinimaArray[i].append([])

    FWHMArray=[0]*len(SampleNames)
    for i in range(len(SampleNames)):
        FWHMArray[i]=[]
        for j in range(len(Sensors)):
            FWHMArray[i].append([])
        
    HeightArray=[0]*len(SampleNames)
    for i in range(len(SampleNames)):
        HeightArray[i]=[]
        for j in range(len(Sensors)):
            HeightArray[i].append([])
                
    FolderDir=os.listdir(DataSet)
    try:
        FileNames.remove('.DS_Store')
    except:
        print()
    NameArray=[0]*len(SampleNames)
    for i in range(len(SampleNames)):
        NameArray[i]=[]
        for j in range(len(Sensors)):
           NameArray[i].append([])

    for i in range(len(FolderDir)):
        if i!=0:
            FigNum=FigNum+1
        FolderName=FolderDir[i]
        Location1=DataSet+"/"+FolderName
        FileDir=os.listdir(Location1)
        for j in range(len(FileDir)):
            FileName=FileDir[j]
            flag=FileName.find(".EP")
            if(flag<0):
                Location2=Location1+"/"+FileName
                Data=open(Location2,"r")
                Data=Data.readlines()
                Data=Data[2:len(Data)]
                [WavArray,TransArray]=Format(Data)
                
                
                if Smooth==True:
                    TransSmooth=[]
                    SmoothMove=(SmoothPoints/2)-0.5
                    SmoothMove=int(SmoothMove)
                    for M in range(SmoothMove,(len(TransArray)-SmoothMove),1):
                        Temp=0
                        for L in range(M-SmoothMove,M+SmoothMove+1,1):
                            Temp=Temp+TransArray[L]
                        TransVal=Temp/SmoothPoints
                        TransSmooth.append(TransVal)
                    
                    WavArray=WavArray[SmoothMove:len(WavArray)-SmoothMove]
                    TransArray=TransSmooth
                if NormaliseQ==True:
                    TransArray=Normalise(TransArray)
                if InterpolateQ==True:
                    [WavArray,TransArray]=Interpolate(WavArray,TransArray,SamplingRate)
                Wavelength=WavArray
                
                Flag1=0
                Flag2=0
                Cut1=[]
                Cut2=[]
                for i in range(len(TransArray)):
                    Temp=Wavelength[i]
                    if Temp>=450 and Flag1==0:
                        Cut1=i
                        Flag1=1
                    if Temp>=900 and Flag2==0:
                        Cut2=i
                        Flag2=1
                if not Cut1:
                    Cut1=0
                if not Cut2:
                    Cut2=len(Wavelength)
                Wavelength=Wavelength[Cut1:Cut2]
                TransArray=TransArray[Cut1:Cut2]
                        
                
                FWHMNum,Height,Baseline=FWHM(Wavelength,TransArray)
            
            # Cut at second differentials of polyfit at either side of lowest first
            
                [WavelengthCut,TransArrayCut]=PolynomialBasedCut(Wavelength,TransArray)
                [TransArrayCut,WavelengthCut]=Reframe(WavelengthCut,TransArrayCut)
            
            # Fit by extreme smoothing of the minima
            
                Minima=SmoothAndSelect(WavelengthCut,TransArrayCut) 
                
                for k in range(len(SampleNames)):
                    flag1=FileName.find(SampleNames[k])
                    if flag1>-1:
                        ArrayNum1=k
                        for k in range(len(Sensors)):
                            flag1=FileName.find(Sensors[k])
                            if flag1>-1:
                                ArrayNum2=k
                                break
            MinimaArray[ArrayNum1][ArrayNum2].append(Minima)
            FWHMArray[ArrayNum1][ArrayNum2].append(FWHMNum)
            HeightArray[ArrayNum1][ArrayNum2].append(Height)   
                # Save Averages
            WavelengthAverage=Wavelength
            if j==0:
                AverageTrans=TransArray
            else:
                for P in range(len(AverageTrans)):
                    AverageTrans[P]=AverageTrans[P]+TransArray[P]
                    if j==(len(FileDir)-1):
                        AverageTrans[P]=AverageTrans[P]/len(FileDir)
        AverageTransArray.append(AverageTrans)
                
    return MinimaArray, FWHMArray, HeightArray, AverageTransArray,WavelengthAverage

# Optosky
def Optosky(DataSet,SampleNames,Sensors,FileNames,Smooth,SmoothPoints,NormaliseQ,InterpolateQ,SamplingRate):
    
    FigNum=0
    MinimaName='null'
    Wavelength=[]
    AverageTransArray=[]
    
    # Set up arrays for data to be inserted into.
    
    MinimaArray=[0]*len(SampleNames)
    for i in range(len(SampleNames)):
        MinimaArray[i]=[]
        for j in range(len(Sensors)):
            MinimaArray[i].append([])

    FWHMArray=[0]*len(SampleNames)
    for i in range(len(SampleNames)):
        FWHMArray[i]=[]
        for j in range(len(Sensors)):
            FWHMArray[i].append([])
        
        HeightArray=[0]*len(SampleNames)
        for i in range(len(SampleNames)):
            HeightArray[i]=[]
            for j in range(len(Sensors)):
                HeightArray[i].append([])
                
    NameArray=[0]*len(SampleNames)
    for i in range(len(SampleNames)):
        NameArray[i]=[]
        for j in range(len(Sensors)):
           NameArray[i].append([])
           
           
# Open each file and read as tab delimited CSV file.
    for i in range(len(FileNames)):
        if i!=0:
            FigNum=FigNum+1
        ArrayCreateFlag=0;
        FileName=FileNames[i]
        Location=DataSet+"/"+FileName
        with open(Location, newline='') as TxtFile:
            Data=csv.reader(TxtFile,delimiter='\t')
            for row in Data:
                Row=row;
                # Use first row to create a blank array into which data will be inserted
                if ArrayCreateFlag==0:
                    [TransmissionArray,TransNumber]=CreateBlank(Row)
                    ArrayCreateFlag=1
                # Since all wavelength (x-axis) should be the same - capture wavelength on first file.
                if i==0:
                    [Wavelength]=WavExtract(Wavelength,Row)
                    WavOrg=Wavelength
                # Pull each row of transmission data and store it in Transmission Array    
                [TransmissionArray]=TransExtract(TransmissionArray,Row,TransNumber)
        # Run through each transmission array and plot    
        for j in range(len(TransmissionArray[0])):
            TransArray=TransmissionArray[0][j]
            if i==0 and j==0:
                Wavelength=Wavelength[1:len(Wavelength)]
            TransArray=TransArray[1:len(TransArray)]

    # Smooth Data if desired
            if Smooth==True:
                TransSmooth=[]
                SmoothMove=(SmoothPoints/2)-0.5
                SmoothMove=int(SmoothMove)
                for M in range(SmoothMove,(len(TransArray)-SmoothMove),1):
                    Temp=0
                    for L in range(M-SmoothMove,M+SmoothMove+1,1):
                        Temp=Temp+TransArray[L]
                    TransVal=Temp/SmoothPoints
                    TransSmooth.append(TransVal)
                if i==0 and j==0:
                    Wavelength=Wavelength[SmoothMove:len(Wavelength)-SmoothMove]
                    WavOrg=Wavelength
                TransArray=TransSmooth
                
            if NormaliseQ==True:
                TransArray=Normalise(TransArray)
            if InterpolateQ==True:
                [Wavelength,TransArray]=Interpolate(WavOrg,TransArray,SamplingRate)
            
            # Find FWHM
            FWHMNum,Height,Baseline=FWHM(Wavelength,TransArray)

            # Cut at second differentials of polyfit at either side of lowest first
            
            [WavelengthCut,TransArrayCut]=PolynomialBasedCut(Wavelength,TransArray)
            [TransArrayCut,WavelengthCut]=Reframe(WavelengthCut,TransArrayCut)
            
            # Fit by extreme smoothing of the minima
            
            Minima=SmoothAndSelect(WavelengthCut,TransArrayCut)              
                      
            # Insert results of fitting into indexable arrays    
            for k in range(len(SampleNames)):
                flag1=FileName.find(SampleNames[k])
                if flag1>-1:
                    ArrayNum1=k
                    break
            for k in range(len(Sensors)):
                flag1=FileName.find(Sensors[k])
                if flag1>-1:
                    ArrayNum2=k
                    break
            # Create arrays for import back to main script
            MinimaArray[ArrayNum1][ArrayNum2].append(Minima)
            FWHMArray[ArrayNum1][ArrayNum2].append(FWHMNum)
            HeightArray[ArrayNum1][ArrayNum2].append(Height)
            NameArray[ArrayNum1][ArrayNum2].append(MinimaName)

            # Save Averages
            
            WavelengthAverage=Wavelength
            if j==0:
                AverageTrans=TransArray
            else:
                for P in range(len(AverageTrans)):
                    AverageTrans[P]=AverageTrans[P]+TransArray[P]
                    if j==(len(TransmissionArray[0])-1):
                        AverageTrans[P]=AverageTrans[P]/len(TransmissionArray[0])
        AverageTransArray.append(AverageTrans)

    return MinimaArray, FWHMArray, HeightArray, AverageTransArray,WavelengthAverage