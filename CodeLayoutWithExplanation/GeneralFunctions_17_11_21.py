# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 09:55:59 2020

@author: IainC
"""

import numpy as np
import warnings
        
def FWHM(Wav,Trans):
    import numpy as np
    Baseline=np.average(Trans[1:101])
    Min=np.min(Trans[1:len(Trans)])
    Height=Baseline-Min
    HM=Min+(Height/2)
    flagdown=0
    flagup=0
    for i in range(30,len(Trans)):
        Value=Trans[i]
        if Value<=HM and flagdown==0:
            flagdown=1;
            Side1=Wav[i]
        if Value>=HM and flagdown==1 and flagup==0 and Wav[i]-Side1>10:
            flagup=1
            Side2=Wav[i]
        if flagup==1 and flagdown==1:
            break
    if flagup==0:
        Side2=0
        Side1=0
    FWHMNum=Side2-Side1
    return FWHMNum, Height, Baseline


def TxtClean(SampleNames): # PCA ONLY
    CleanName=[]
    for i in range(len(SampleNames)):
        Name=SampleNames[i]
        for j in range(len(Name)-1):
            Symbol=Name[j]
            if Symbol=='_' or Symbol=='-':
                Name=Name[0:j]+Name[j+1:len(Name)]
        CleanName.append(Name)
    return CleanName


def CreateBlank(Data):
    # Create an array of blank arrays using data to define the length
    TransNumber=len(Data)-1;
    TransArray=[0]*TransNumber
    for i in range(TransNumber):
        TransArray[i]=[]
        
    return([TransArray],TransNumber)

def WavExtract(Wavelength,Row):
    # Pull wavelength values from the optosky txt files, wavelength is always row 0.
    Wav=Row[0];
    Wav=float(Wav)
    Wavelength.append(Wav)
    return [Wavelength]

def TransExtract(TransmissionArray,Row,TransNumber):
  for i in range((len(Row)-TransNumber),len(Row)):
      TransVal=Row[i]
      TransVal=float(TransVal)
      TransmissionArray[0][i-1].append(TransVal)
  return  ([TransmissionArray])
 
def RecogniseInputs(FileNames1):
    Sensors=[]
    SampleNames=[]
    Cut=0
    for i in range(len(FileNames1)):
        Counter=0
        Name=FileNames1[i]
        for j in range (len(Name)):
            Letter=Name[j]
            if Letter=='_':
                Counter=Counter+1
            if Letter != '_' and Counter==1:
                Counter=0
            if Counter>1:
                Cut=j-(Counter-1)
                break
        if Cut!=0:
            FileNames1[i]=Name[0:Cut]
            
    for i in range(len(FileNames1)):
        Counter=0
        Name=FileNames1[i]
        for j in range(len(Name)):
            Letter=Name[j]
            if Letter=='_':
                Counter=Counter+1
            if Counter==2:
                Sensor=Name[0:j]
                Sample=Name[j+1:len(Name)]
                CheckSensor= Sensor in Sensors
                CheckSample= Sample in SampleNames
                if CheckSensor == False:
                    Sensors.append(Sensor)
                if CheckSample == False:
                    SampleNames.append(Sample)
                break 
    return(Sensors,SampleNames,FileNames1)
     
    
def Format(Data):
   WaveArray=[]
   TransArray=[]
   for i in range(len(Data)):
       Values=Data[i]
       Wavelength=float(Values[1:9])
       Transmission=float(Values[9:len(Values)])
       WaveArray.append(Wavelength)
       TransArray.append(Transmission)
   for j in range(len(WaveArray)):
       Value=WaveArray[j]
       if Value>=460:
           Cut=j
           break
   WaveArray=WaveArray[Cut:len(WaveArray)]
   TransArray=TransArray[Cut:len(TransArray)]
    

   return WaveArray,TransArray



def FindMinimaError(MinimaArray,i,j,Avg):
    Sum=0
    
    Sum=(np.max(MinimaArray[i][j])-np.min(MinimaArray[i][j]))/2
    if Sum<0:
        Sum=Sum*-1
    
    Error=np.sqrt(Sum)
    
    return Error
    
        
def IsolateNames(Names):
    SampleArray=[]
    for i in range(len(Names)):
        Counter=0
        Name=Names[i]
        for j in range(len(Name)):
            Char=Name[j]
            if Char=='(' and Counter==0:   
                Counter=Counter+1
                cut_start=j
            if Counter==1:
                Test=Char.isnumeric()
                if Test==True:
                    Counter=Counter+1
            if Counter==2 and Char==')':
                Sample=Name[0:cut_start]
                SampleArray.append(Sample)


    return SampleArray


            
            
   
        
        
                    
                     
                     
                     
                     
                     
                     
                     

                     
                     

  
    
            
        
        
        
        
    