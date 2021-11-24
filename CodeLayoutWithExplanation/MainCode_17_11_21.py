# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

"""
import numpy as np
import matplotlib.pyplot as plt


import os
import csv
import math

from GeneralFunctions_17_11_21 import RecogniseInputs
from GeneralFunctions_17_11_21 import FindMinimaError
from GeneralFunctions_17_11_21 import IsolateNames

from Imports_17_11_21 import SpectraWiz
from Imports_17_11_21 import Optosky

from PlottingFunctions_17_11_21 import OverlayPlot

from PCAFunctions_17_11_21 import Do_PCA

# DataSet should be the name of the folder that is being extracted from.

DataSet="08_09_21_CreatineRepeats" 

# Define what format the data will be in - Spectrawiz or Optosky

SpectraWiz_Select=True
OptoSky_Select=False

# Do you want smoothing and if so how much?

Smooth=True
SmoothPoints=3

Interpolate=True
SamplingRate=0.3
Normalise=True

# Choose overlaying plots

OverlaySensors=True
OverlaySamples=False
AllPlot=True

# Turn off all graphs plotting with minima and errors attached
AllGraphs=True

Do_PCA_Q=False









# Setup empty variables for later and close all figures.
plt.close('all')

FigNum=0;
SampleNamesExt=[]
MinimaOrder=[]

# Search Defined directory

FileNames=os.listdir(DataSet);
FileNamesEdit=FileNames[:]

# Recognise sample and sensor names based off of defined data layout. 
# Sq100_AlBare_Di1__AnythingElse

[Sensors,SampleNames,FileNames1]=RecogniseInputs(FileNamesEdit);

# Run either SpectraWiz or Optosky data intake. Returns FWHM and minima or each reading.

if SpectraWiz_Select==True:
    [MinimaArray,FWHMArray,HeightArray,AverageTransArray,WavelengthAverage]=SpectraWiz(DataSet,SampleNames,Sensors,FileNames,Smooth,SmoothPoints,Normalise,Interpolate,SamplingRate)
    
if OptoSky_Select==True:
    [MinimaArray,FWHMArray,HeightArray,AverageTransArray,WavelengthAverage]=Optosky(DataSet,SampleNames,Sensors,FileNames,Smooth,SmoothPoints,Normalise,Interpolate,SamplingRate)


# Average the data above to get the best estimation for minima over the readings that have been taken
    # Store this data.

AverageFWHMArray=[]
AverageHeightArray=[]
AverageMinimaArray=[]
MinimaErrorArray=[]

for i in range(len(FWHMArray)):
    for j in range(len(FWHMArray[0])):
        if MinimaArray[i][j]:
            AverageFWHM=np.average(FWHMArray[i][j])
            AverageFWHMArray.append(AverageFWHM)
            AverageHeight=np.average(HeightArray[i][j])
            AverageHeightArray.append(AverageHeight)
            AverageMinima=np.average(MinimaArray[i][j])
            Error=FindMinimaError(MinimaArray,i,j,AverageMinima)
            MinimaErrorArray.append(Error)
            AverageMinimaArray.append(AverageMinima)
            MinimaOrder.append(Sensors[j]+SampleNames[i])


# Set up an expanded list of sample names in order to label panda's dataframe for PCA    
for i in range(len(SampleNames)):
    for j in range(len(MinimaArray[i])):
        if MinimaArray[i][j]:
            for k in range(len(MinimaArray[i][j])):
                SampleNamesExt.append(SampleNames[i])
                          
# Write minima and FWHM to CSV file
            
Rows=[]

for i in range(len(AverageMinimaArray)):
    if math.isnan(AverageMinimaArray[i])==False:
        Row=[MinimaOrder[i],AverageMinimaArray[i],AverageFWHMArray[i],AverageHeightArray[i]]
        Rows.append(Row)  
Slash='/'    
NewFileName='CSVFiles' + Slash + DataSet + '.csv'
with open(NewFileName,'w') as newfile:
    Writer=csv.writer(newfile)
    Writer.writerow(['FileName','Average Minima (nm)','Average FWHM (nm)','Average Height (%T)'])
    for i in range(len(Rows)):
        Writer.writerow(Rows[i])
        
# Save Figures - Raw
        #Create Directory for Figures
Current=os.getcwd()
New=Current+Slash+'Figures'+Slash+DataSet
if os.path.isdir(New)==False:
    os.makedirs(New)
NewPathMinFig=New+Slash+'Raw_Date_with_Minima'
if os.path.isdir(NewPathMinFig)==False:
    os.mkdir(NewPathMinFig)
else:
    NewPathMinFig=Current+Slash+'Figures'+Slash+DataSet+Slash+'Raw_Date_with_Minima'
for i in plt.get_fignums():
    FigTemp=plt.figure(i)
    FigTemp.set_size_inches(15, 8)
    Save=NewPathMinFig+Slash+plt.figure(i).axes[0].get_title()
    plt.savefig(Save)

# Save Figure - Average
Current=os.getcwd()
New=Current+Slash+'Figures'+Slash+DataSet
if os.path.isdir(New)==False:
    os.makedirs(New)
NewPathMinFig=New+Slash+'Averaged_Data_with_Minima'
if os.path.isdir(NewPathMinFig)==False:
    os.mkdir(NewPathMinFig)
else:
    NewPathMinFig=Current+Slash+'Figures'+Slash+DataSet+Slash+'Averaged_Data_with_Minima'

if AllGraphs==True:
    for P in range(len(FileNames)):
        FigNum=plt.gcf().number+1
        FigTemp=plt.figure(FigNum)
        TitleTxt=FileNames[P].replace('.txt','')
        TitleTxt=TitleTxt+' - Average' 
        Average=plt.plot(WavelengthAverage,AverageTransArray[P],'b',label='Averaged Raw Data', zorder=10)
        # Find corresponding Minima
        for i in range(len(SampleNames)):
            Name=SampleNames[i]
            Flag1=FileNames[P].find(Name)
            if Flag1>-1:
                SampleNum=i
                break
        for j in range(len(Sensors)):
            Name2=Sensors[j]
            Flag2=FileNames[P].find(Name2)
            if Flag2>-1:
                SensorNum=j
                break
        for k in range(len(MinimaOrder)):
            Flag3=MinimaOrder[k].find(SampleNames[SampleNum])
            if Flag3>-1:
                Flag4=MinimaOrder[k].find(Sensors[SensorNum])
                if Flag4>-1:
                    MinPlotNum=k
        MinLimit=0
        MaxLimit=100

        MinimaLine=plt.plot([AverageMinimaArray[MinPlotNum],AverageMinimaArray[MinPlotNum]],[MinLimit,MaxLimit],'r',label='Average Minima', zorder=10 )
        plt.title(TitleTxt,fontsize=25, fontweight="bold")
    
        MinimaTxt=np.round(AverageMinimaArray[MinPlotNum],3)
        MinimaTxt=str(MinimaTxt)
        Write= 'Average Minima:'+' '+MinimaTxt+'nm'
        plt.text(675,10,Write,fontsize=15)
    
    
        Error=MinimaErrorArray[MinPlotNum]
        Error=np.round(Error,3)
        ErrorTxt=str(Error)
        Write='Error:'+' '+'+/-'+' '+ErrorTxt+'nm'
        plt.text(690,5,Write,fontsize=15)
        if SpectraWiz_Select==True:
            if Normalise==False:
                plt.axis([460,900,0,100])
            if Normalise==True:
                plt.axis([460,900,0,1])
        if OptoSky_Select==True:
            if Normalise==False:
                plt.axis([450,750,0,100])
            if Normalise==True:
                plt.axis([450,750,0,1])
                
    
        plt.xlabel("Wavelength (nm)", fontsize=20)
        plt.ylabel("Transmission (%)", fontsize=20)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        FigTemp.set_size_inches(15, 8)
    
        plt.legend(handles=[Average[0],MinimaLine[0]],fontsize=15)
    
        Save=NewPathMinFig+Slash+plt.figure(FigNum).axes[0].get_title()
        plt.savefig(Save)


OverlayPlot(WavelengthAverage,AverageTransArray,AverageMinimaArray,FileNames,OverlaySensors,OverlaySamples,AllPlot,SampleNames,Sensors,DataSet,OptoSky_Select,SpectraWiz_Select,Normalise)

if Do_PCA_Q==True:
    SampleNameSimple=IsolateNames(SampleNames)
    Do_PCA(AverageMinimaArray,MinimaOrder,Sensors,SampleNameSimple)
    
