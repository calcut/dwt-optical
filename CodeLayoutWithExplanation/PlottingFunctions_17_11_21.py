
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:16:36 2021

@author: IainC
"""

# Plotting Functions

def Plotter(WavArray,TransArray,FigNum,Name,i,Minima,MinimaFit,MinimaArea,OptoSky=None):
    
    import matplotlib.pyplot as plt
    
    plt.figure(FigNum)
    
    # plot raw data and the minima as a red line

    plt.axis([400,900,0,100])
    MinimaLineY=[0,100]
    MinimaLineX=[Minima,Minima]    
       
    RawData=plt.plot(WavArray,TransArray,'b',label='Raw Data',zorder=3)
    Fitted=plt.plot(MinimaLineX,MinimaLineY,'r',label='Fitted Minima', zorder=10 )
      
    plt.title(Name[i].replace('.txt',''),fontsize=25, fontweight="bold")
    plt.xlabel("Wavelength (nm)", fontsize=20)
    plt.ylabel("Transmission (%)", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(handles=[MinimaFit[0],MinimaArea[0],RawData[0],Fitted[0]],fontsize=15)
    return FigNum


def PlotterPoly(Wavelength,TransArray,Inflections,FittedValues,FigNum,i,Name,PolyPlot):
    
    if PolyPlot==1:
        import matplotlib.pyplot as plt

        plt.figure(FigNum)
    
        # plot raw data and the minima as a red line

        plt.axis([400,900,0,100])
    
        InflectionPlots=[]
        for j in range(len(Inflections)):
            Inf=[]
            Inf.append(Inflections[j])
            Inf.append(Inflections[j])
            InflectionPlots.append(Inf)
            InfY=[0,100]
            for j in range(len(InflectionPlots)):   
                plt.plot(InflectionPlots[j],InfY,'g',label='InflectionPoints_%s'% j, zorder=10 )
        
        
        plt.plot(Wavelength,TransArray,'b',label='Raw Data',zorder=3)
        plt.plot(Wavelength,FittedValues,'r',label='Fitted Polynomial',zorder=5,linewidth=2)  
    
    
        plt.title(Name[i].replace('.txt',''),fontsize=25, fontweight="bold")
        plt.xlabel("Wavelength (nm)", fontsize=20)
        plt.ylabel("Transmission (%)", fontsize=20)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.legend(fontsize=15)
        FigNum=(plt.gcf().number+1)
    return FigNum

def MultiFit_Plotter(Wavelength,TransArray,FittedValues,Minima,FigNum,Name,MinimaName):
    
    import matplotlib.pyplot as plt
    
    Title=Name.replace('.txt','')
    Title=Title+'with'+MinimaName
    
    plt.figure(FigNum)
    
    plt.plot(Wavelength,TransArray,'b')
    plt.plot(Wavelength,FittedValues,'r')
    plt.plot([Minima,Minima],[0,100])
    plt.title(Title)
    plt.xlabel("Wavelength (nm)", fontsize=20)
    plt.ylabel("Transmission (%)", fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.legend(fontsize=15)

    FigNum=FigNum+1
    
    return FigNum


def OverlayPlot(WavelengthAverage,AverageTransArray,AverageMinimaArray,FileNames,OverlaySensors,OverlaySamples,AllPlot,Samples,Sensors,DataSet,OptoSky_Select,SpectraWiz_Select,Normalise):
    import matplotlib.pyplot as plt
    import os
    
    Slash='/'
    Current=os.getcwd()
    New=Current+Slash+'Figures'+Slash+DataSet
    if os.path.isdir(New)==False:
        os.makedirs(New)
    NewPathMinFig=New+Slash+'OverlayedPlots'
    if os.path.isdir(NewPathMinFig)==False:
        os.mkdir(NewPathMinFig)
    else:
        NewPathMinFig=Current+Slash+'Figures'+Slash+DataSet+Slash+'OverlayedPlots'
    
    if OverlaySensors==True:
        for i in range(len(Sensors)):
            FigNum=plt.gcf().number+1
            LegendArray=[]
            Sensor=Sensors[i]
            Sensor=Sensor+'_'
            for j in range(len(FileNames)):
                FileName=FileNames[j]
                Flag=FileName.find(Sensor)
                if Flag>-1:
                    for k in range(len(Samples)):
                        Sample=Samples[k]
                        Sample=Sample+'_'
                        Flag=FileName.find(Sample)
                        if Flag>-1:
                            LegendArray.append(Sample[0:(len(Sample)-1)])
                            
                    FigTemp=plt.figure(FigNum)
                    plt.plot(WavelengthAverage,AverageTransArray[j],label=LegendArray[len(LegendArray)-1])
                    if OptoSky_Select==True:
                        if Normalise==False:
                            plt.axis([450,750,0,100])
                        if Normalise==True:
                            plt.axis([450,750,0,1])
                    if SpectraWiz_Select==True:
                        if Normalise==False:
                            plt.axis([460,900,0,100])
                        if Normalise==True:
                            plt.axis([460,900,0,1])
                    plt.xlabel("Wavelength (nm)", fontsize=20)
                    plt.ylabel("Transmission (%)", fontsize=20)
                    plt.xticks(fontsize=18)
                    plt.yticks(fontsize=18)
                    FigTemp.set_size_inches(15, 8)
                    plt.legend(LegendArray,fontsize=15)
                    plt.title(Sensor[0:(len(Sensor)-1)],fontsize=25, fontweight="bold")
                    Save=NewPathMinFig+Slash+plt.figure(FigNum).axes[0].get_title()
                    plt.savefig(Save)
    if OverlaySamples==True:
        for i in range(len(Samples)):
            FigNum=plt.gcf().number+1
            LegendArray=[]
            Sample=Samples[i]
            Sample=Sample+'_'
            for j in range(len(FileNames)):
                FileName=FileNames[j]
                Flag=FileName.find(Sample)
                if Flag>-1:
                    for k in range(len(Sensors)):
                        Sensor=Sensors[k]
                        Sensor=Sensor+'_'
                        Flag=FileName.find(Sensor)
                        if Flag>-1:
                            LegendArray.append(Sensor[0:(len(Sensor)-1)])
                            
                    FigTemp=plt.figure(FigNum)
                    plt.plot(WavelengthAverage,AverageTransArray[j])
                    if OptoSky_Select==True:
                        if Normalise==False:
                            plt.axis([450,750,0,100])
                        if Normalise==True:
                            plt.axis([450,750,0,1])
                    if SpectraWiz_Select==True:
                        if Normalise==False:
                            plt.axis([460,900,0,100])
                        if Normalise==True:
                            plt.axis([460,900,0,1])
                    plt.xlabel("Wavelength (nm)", fontsize=20)
                    plt.ylabel("Transmission (%)", fontsize=20)
                    plt.xticks(fontsize=18)
                    plt.yticks(fontsize=18)
                    FigTemp.set_size_inches(15, 8)
                    plt.legend(LegendArray,fontsize=15)
                    plt.title(Sample[0:(len(Sample)-1)],fontsize=25, fontweight="bold") 
                    Save=NewPathMinFig+Slash+plt.figure(FigNum).axes[0].get_title()
                    plt.savefig(Save)
                    
    if AllPlot==True:
        FigNum=plt.gcf().number+1
        LegendArray=[]
        for i in range(len(FileNames)):
            Trans=AverageTransArray[i]
            Wav=WavelengthAverage
            FigTemp=plt.figure(FigNum)
            plt.plot(Wav,Trans)
            LegendArray.append(FileNames[i])
            plt.title('All Files in Folder',fontsize=25,fontweight='bold')
            plt.xlabel("Wavelength (nm)", fontsize=30)
            plt.ylabel("Transmission (%)", fontsize=30)
            if OptoSky_Select==True:
                if Normalise==False:
                    plt.axis([450,750,0,100])
                if Normalise==True:
                    plt.axis([450,750,0,1])
            if SpectraWiz_Select==True:
                if Normalise==False:
                    plt.axis([460,900,0,100])
                if Normalise==True:
                    plt.axis([460,900,0,1])
            plt.xticks(fontsize=30)
            plt.yticks(fontsize=30)
            FigTemp.set_size_inches(15, 8)
            plt.legend(LegendArray,fontsize=15)
                             