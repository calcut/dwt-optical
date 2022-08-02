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

from GeneralFunctions_17_06_22 import RecogniseInputs
from GeneralFunctions_17_06_22 import FindMinimaError
from GeneralFunctions_17_06_22 import IsolateNames

from Imports_17_06_22 import SpectraWiz
from Imports_17_06_22 import Optosky

from PlottingFunctions_17_06_22 import OverlayPlot

from PCAFunctions_17_06_22 import Do_PCA

def analyse_datasets(DataSet,SpectraWiz_Select,OptoSky_Select,TypeM,WMin,WMax,Smooth,SmoothPoints,
                 Interpolate,SamplingRate,Normalise,OverlaySensors,OverlaySamples,AllPlot,AllGraphs,
                 ShowMinimaLine,Do_PCA_Q,OutputSmoothedCSVFile):
    # DataSet should be the name of the folder that is being extracted from.
    
# =============================================================================
#     DataSet="data" 
#     
#     # Define what format the data will be in - Spectrawiz or Optosky
#     
#     SpectraWiz_Select=True
#     OptoSky_Select=False
#     
#     # Max or Min?
#     TypeM="Max"
#     
#     # Wavelength Range? (largest can be 400 to 999)
#     WMin = 400
#     WMax = 950
#     
#     # Do you want smoothing and if so how much?
#     
#     Smooth=True
#     SmoothPoints=3
#     
#     Interpolate=False
#     SamplingRate=0.3
#     Normalise=False
#     
#     # Choose overlaying plots
#     
#     OverlaySensors=False
#     OverlaySamples=False
#     AllPlot=True
#     ShowMinimaLine = False
#     
#     # Turn off all graphs plotting with minima and errors attached
#     AllGraphs=True
#     
#     Do_PCA_Q=False
#     
#     OutputSmoothedCSVFile=True
# =============================================================================
    
    
    
    #####################################
    ## Create Metadata file to explain ##
    ## data processing                 ##
    #####################################
    
    MetaString = ''
    newline = '\n'
    countModifications = 0
    boolModified = False
    
    if (Smooth or Interpolate or Normalise):
        boolModified = True
    
    if WMin < 400:
        WMin = 400
    
    if WMax > 999:
        WMax = 999
    
    if WMin > WMax:
        WMin = 450
        WMax = 950
    
    
    ## Description of which tool was used to collect data and all preprocessing
    if SpectraWiz_Select:
         MetaString += 'Data Collected With: SpectraWiz' 
         MetaString += newline + newline
         MetaString += 'Preprocessing:' + newline
         MetaString += '0) The data is cut from ' + str(WMin) + ' to ' + str(WMax) + ' nm' + newline 
    else:
        if OptoSky_Select:
            MetaString += 'Data Collected With: OptoSky' + newline + newline
            MetaString += 'Preprocessing:' + newline 
            MetaString += ' 0) The first datapoint is removed' + newline 
        else:
            MetaString += 'Data Collected With: Unknown' + newline + newline
            MetaString += 'Preprocessing:' + newline      
            
    if boolModified:
        countModifications += 1
        if Smooth:
            MetaString += str(countModifications) + ') ' 
            MetaString += str(SmoothPoints) + '-points average smoothing' 
            MetaString += newline
            countModifications += 1
        
        if Normalise:
             MetaString += str(countModifications) + ') ' 
             MetaString += 'Normalized by dividing all points by the ' 
             MetaString += 'maximum transmission value' + newline
             countModifications += 1
       
        if Interpolate:
             MetaString += str(countModifications) + ') ' 
             MetaString += 'Linear interpolation by ' 
             MetaString += str(SamplingRate) + ' nm ' + newline
             countModifications += 1 
    ## END desciption of preprocessing        
    
    
    MetaString += newline
    MetaString += 'After preprocessing, the minima, FWHM, and height are calculated.' 
    MetaString += newline + newline
    
    ## Description of Minima Finding
    MetaString += 'Minima Finding:' + newline
    MetaString += 'For each spectra, a minima is calculated. '
    if SpectraWiz_Select:
        MetaString += 'For each .TRM file (whether separate or from an .EP), '
    if OptoSky_Select:
        MetaString += 'For each spectra within a .TXT output file, '
    MetaString += 'the literal mimina of the data is found and the data is cut '
    MetaString += 'around this minima by fitting the entire spectra with a high '
    MetaString += 'order polynomial (polyfit function). The second derivative ' 
    MetaString += 'of this fit is then used to find the inflection points and the data '
    MetaString += 'is then cut at these inflection points. Once this cut has taken place, '
    MetaString += 'the remaining peak (trough) is levelled out as to not bias any '
    MetaString += 'following steps. The remaining subset of data is 30-point '
    MetaString += 'smoothed and the minimum value is taken from this smoothed '
    MetaString += 'section. The CSV output is the averaged minima '
    if SpectraWiz_Select:
        MetaString += 'of all .TRM from an .EP file (or if not from episodic data '
        MetaString += 'capture, just the single minima from the .TRM). '
    if OptoSky_Select:
        MetaString += 'of all spectra in the OptoSky .TXT file (or if the file only  '
        MetaString += 'contains a single measurement, just the single minima). '
    MetaString += newline + newline
    ## End description of minima finding
    
    ## Description of FWHM and Height Finding
    MetaString += 'FWHM and Height Finding:' + newline
    MetaString += 'The y-value of first 100 datapoints (after preprocessing) are '
    MetaString += 'averaged to give a baseline. The absolute minima (not fit minima) '
    MetaString += 'is subtracted from this baseline to find the height of the spectra. '
    MetaString += 'The 2 wavelength values closest to half this y-value are then found '
    MetaString += 'and the difference between these two wavelength values are the FWHM. '
    MetaString += 'The CSV output is the averaged FWHM and averaged height '
    if SpectraWiz_Select:
        MetaString += 'of all .TRM from an .EP file (or if not from episodic data '
        MetaString += 'capture, just the single FWHM and height from the .TRM). '
    if OptoSky_Select:
        MetaString += 'of all spectra in the OptoSky .TXT file (or if the file only  '
        MetaString += 'contains a single measurement, just the single FWHM and height). '
    MetaString += newline + newline
    ## END Description of FWHM Finding
    
    ## Description of Averaged_Data_with_Minima Figures
    MetaString += 'The Averaged_Data_with_Minima figures are made by averaging '
    MetaString += 'all y-values at each wavelength of all '
    if SpectraWiz_Select:
        MetaString += '.TRM from an .EP '
        MetaString += 'file (or if not from episodic data capture, '
    if OptoSky_Select:
        MetaString += 'spectra in the OptoSky .TXT '
        MetaString += '.TXT file (or if the file only contains a single measurement, '
    MetaString += 'the figure is only the data from the single spectra). '
    MetaString += 'The vertical line is of the calculated minima from the Minima '
    MetaString += 'Finding process, where the "Error" is calculated by 1/2 * [(max minima) '
    MetaString += '- (smallest minima)] '
    if SpectraWiz_Select:
        MetaString += 'of all .TRM from an .EP file (or if not from episodic data '
        MetaString += 'capture, the "Error" is 0). '
    if OptoSky_Select:
        MetaString += 'of all spectra in the OptoSky .TXT file (or if the file only  '
        MetaString += 'contains a single measurement, the "Error" is 0). '
    MetaString += newline + newline
    ## END Description of Averaged_Data_with_Minima Figures
    
    MetaString += 'NOTE: The preprocessing of the data will affect calculations '
    MetaString += 'for the minima, height, and FWHM.'
    
    ###############################
    ## END METADATA FILE WRITING ##
    ###############################
    
    # Setup empty variables for later and close all figures.
    plt.close('all')
    
    FigNum=0;
    SampleNamesExt=[]
    MinimaOrder=[]
    
    # Search Defined directory
    
    
    folderpathway = DataSet[0:DataSet.rfind('/')]
    foldername = DataSet[DataSet.rfind('/')+1:len(DataSet)]
    #print(str(DataSet))
    #print(str(folderpathway))
    #print(str(foldername))
    FileNames=os.listdir(DataSet)
    
    try:
        FileNames.remove('.DS_Store')
    except:
        catched = 1
        
    FileNamesEdit=FileNames[:]
    
    # Recognise sample and sensor names based off of defined data layout. 
    # Sq100_AlBare_Di1__AnythingElse
    
    [Sensors,SampleNames,FileNames1]=RecogniseInputs(FileNamesEdit);
    
    # Run either SpectraWiz or Optosky data intake. Returns FWHM and minima or each reading.
    
    if SpectraWiz_Select==True:
        [MinimaArray,FWHMArray,HeightArray,AverageTransArray,WavelengthAverage]=SpectraWiz(DataSet,SampleNames,Sensors,FileNames,Smooth,SmoothPoints,Normalise,Interpolate,SamplingRate,TypeM,WMin,WMax)
        
    if OptoSky_Select==True:
        [MinimaArray,FWHMArray,HeightArray,AverageTransArray,WavelengthAverage]=Optosky(DataSet,SampleNames,Sensors,FileNames,Smooth,SmoothPoints,Normalise,Interpolate,SamplingRate,TypeM,WMin,WMax)
    
    
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
    Current=folderpathway
    New=Current+Slash+foldername+'_CSVFiles'
    if os.path.isdir(New)==False:
        os.makedirs(New)
   
    NewFileName=folderpathway+Slash+foldername+'_CSVFiles' + Slash + foldername + '.csv'
    MetaFileName= folderpathway+Slash+foldername+'_CSVFiles' + Slash + foldername +'_csv_metadata.txt'
    with open(NewFileName,'w') as newfile:
        Writer=csv.writer(newfile)
        Writer.writerow(['FileName','Average Minima (nm)','Average FWHM (nm)','Average Height (%T)'])
        for i in range(len(Rows)):
            Writer.writerow(Rows[i])
     
    # Output Metafile
    metaF = open(MetaFileName,'w')
    metaF.write(MetaString)
    metaF.close()
    
    # Save Figures - Raw
            #Create Directory for Figures
    Current=folderpathway
    New=Current+Slash+foldername+'_Figures'+Slash+foldername
    if os.path.isdir(New)==False:
        os.makedirs(New)
    
    # Output Metafile
    MetaFileName2 = Current+Slash+foldername+'_Figures'+Slash+foldername+'_figures_metadata.txt'
    metaF = open(MetaFileName2,'w')
    metaF.write(MetaString)
    metaF.close()
    
    NewPathMinFig=New+Slash+'Raw_Date_with_Minima'
    if os.path.isdir(NewPathMinFig)==False:
        os.mkdir(NewPathMinFig)
    else:
        NewPathMinFig=Current+Slash+foldername+'_Figures'+Slash+foldername+Slash+'Raw_Date_with_Minima'
    for i in plt.get_fignums():
        FigTemp=plt.figure(i)
        FigTemp.set_size_inches(15, 8)
        Save=NewPathMinFig+Slash+plt.figure(i).axes[0].get_title()
        plt.savefig(Save)
    
    # Save Figure - Average
    #Current=os.getcwd()
    Current=folderpathway
    New=Current+Slash+foldername+'_Figures'+Slash+foldername
    if os.path.isdir(New)==False:
        os.makedirs(New)
    NewPathMinFig=New+Slash+'Averaged_Data_with_Minima'
    if os.path.isdir(NewPathMinFig)==False:
        os.mkdir(NewPathMinFig)
    else:
        NewPathMinFig=Current+Slash+foldername+'_Figures'+Slash+foldername+Slash+'Averaged_Data_with_Minima'
    
    if AllGraphs==True:
        for P in range(len(FileNames)):
            FigNum=plt.gcf().number+1
            FigTemp=plt.figure(FigNum)
            TitleTxt=FileNames[P].replace('.txt','')
            TitleTxt=TitleTxt+' - Average' 
            
            if (TypeM=="Max"):                    
                for i in range(len(AverageTransArray[P])):
                    AverageTransArray[P][i]= AverageTransArray[P][i]*(-1)
            absMin = min(AverageTransArray[P])
            Average=plt.plot(WavelengthAverage,AverageTransArray[P],'b',label='Averaged Raw Data', zorder=10)
            
            if min(WavelengthAverage) > WMin:
                WMin =  round(min(WavelengthAverage))
                
            if max(WavelengthAverage) < WMax:
                WMax = round(max(WavelengthAverage))
            
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
            
            if ShowMinimaLine:
                MinimaLine=plt.plot([AverageMinimaArray[MinPlotNum],AverageMinimaArray[MinPlotNum]],[MinLimit,MaxLimit],'r',label='Average Minima', zorder=10 )
                MinimaTxt=np.round(AverageMinimaArray[MinPlotNum],3)
                if (TypeM=="Max"):
                    MinimaTxt=MinimaTxt
                MinimaTxt=str(MinimaTxt)
                Write= 'Average Minima:'+' '+MinimaTxt+'nm'
                plt.text(675,10,Write,fontsize=15)
                Error=MinimaErrorArray[MinPlotNum]
                Error=np.round(Error,3)
                ErrorTxt=str(Error)
                Write='Error:'+' '+'+/-'+' '+ErrorTxt+'nm'
                plt.text(690,5,Write,fontsize=15)
            
            plt.title(TitleTxt,fontsize=25, fontweight="bold")
        
            
            if SpectraWiz_Select==True:
                if Normalise==False:
                    plt.axis([WMin,WMax,0,100])
                if Normalise==True:
                    plt.axis([WMin,WMax,0,1])
            if OptoSky_Select==True:
                if Normalise==False:
                    plt.axis([WMin,WMax,0,100])
                if Normalise==True:
                    plt.axis([WMin,WMax,0,1])
                    
        
            plt.xlabel("Wavelength (nm)", fontsize=20)
            plt.ylabel("Transmission (%)", fontsize=20)
            plt.xticks(fontsize=18)
            plt.yticks(fontsize=18)
            FigTemp.set_size_inches(15, 8)
            
            if ShowMinimaLine:
                plt.legend(handles=[Average[0],MinimaLine[0]],fontsize=15)
            else:
                plt.legend(handles=[Average[0]],fontsize=15)
        
            Save=NewPathMinFig+Slash+plt.figure(FigNum).axes[0].get_title()
            plt.savefig(Save)
            
            Title2=FileNames[P].replace('.txt','')
            
            if(OutputSmoothedCSVFile):
                NewFileNameSmoothedSpectra=folderpathway+Slash+foldername+'_CSVFiles' + Slash + Title2 + '_smoothed_average_spectra.csv'           
                smoothedFile = open(NewFileNameSmoothedSpectra,'w')
                
                for i in range(len(WavelengthAverage)):               
                    newValue=str(WavelengthAverage[i])+","+str(AverageTransArray[P][i])+newline
                    smoothedFile.write(newValue)
                    
                smoothedFile.close()
    
    OverlayPlot(foldername,Current,WavelengthAverage,AverageTransArray,AverageMinimaArray,FileNames,OverlaySensors,OverlaySamples,AllPlot,SampleNames,Sensors,foldername,OptoSky_Select,SpectraWiz_Select,Normalise,WMin,WMax)
    
    if Do_PCA_Q==True:
        SampleNameSimple=IsolateNames(SampleNames)
        Do_PCA(AverageMinimaArray,MinimaOrder,Sensors,SampleNameSimple)
    
    return 1
