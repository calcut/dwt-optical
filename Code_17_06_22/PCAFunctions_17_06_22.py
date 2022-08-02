# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:15:38 2021

@author: IainC
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn import preprocessing
from sklearn.decomposition import PCA

# PCA Functions
def Do_PCA(AverageMinimaArray,MinimaOrder,Sensors,SampleSimple):
    
    #PCAFrame=pd.DataFrame(columns=[*SampleSimple],index=Sensors,dtype=np.float)
    PCAFrame=pd.DataFrame(columns=Sensors,index=[*SampleSimple],dtype=np.float) 
   
    OneName=[]
    for i in range(len(SampleSimple)):
        Name1=SampleSimple[i]
        if Name1 not in OneName:
            OneName.append(Name1)
      
    for j in Sensors: #switched j and i
        for i in OneName:
            Counter=0
            for k in range(len(MinimaOrder)):
                Name=MinimaOrder[k]
                if i in Name:
                    if j in Name:
                        Temp=PCAFrame.loc[i,j]
                        if isinstance(Temp,np.floating)==True:
                            PCAFrame.loc[i,j]=AverageMinimaArray[k]
                        else:
                            Temp.iloc[Counter]=AverageMinimaArray[k]
                        Counter=Counter+1
                            
    Scaler=preprocessing.StandardScaler()
    PCAScaled=Scaler.fit_transform(PCAFrame.loc[:].values)
    PCAFinal=PCA()
    PCAData=PCAFinal.fit_transform(PCAScaled)
    
    PrincipleN=PCAData.shape[1]
    PCName=[]
    for i in range(PrincipleN):
        PC='Principle Component'+str(i+1)
        PCName.append(PC)
    
    PCADataFinal=pd.DataFrame(data=PCAData,columns=PCName)
    Varience=np.round(PCAFinal.explained_variance_ratio_*100, decimals=1)
    
    num=plt.gcf().number+1
    plt.figure(num)
    Components=PCAFinal.explained_variance_ratio_
    Components=Components*100
    PCAName=['PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8']
    PCAName=PCAName[0:len(Components)]
    plt.bar(PCAName,Components)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.title('Scree Plot', fontsize=25,fontweight='bold')
    
    num=plt.gcf().number+1
    plt.figure(num)
    plt.title('PCA',fontsize=30,fontweight='bold')
    plt.xlabel('PC1',fontsize=25)
    plt.ylabel('PC2',fontsize=25)
    
    colours=['r','g','b','c','m','y','k']
    colours=colours[0:len(OneName)]
    Counter=0
    for OneName, color in zip(OneName, colours):
        Counter=Counter+1
        Indexs=PCAFrame.index.get_loc(OneName)
        IndexStart=Indexs.start
        IndexStop=Indexs.stop
        Temp1=PCADataFinal.loc[IndexStart:IndexStop-1,'Principle Component1']
        Temp2=PCADataFinal.loc[IndexStart:IndexStop-1,'Principle Component2']
        Numbers=Temp1.index._data
        Indicies=[]
        for i in range(len(Numbers)):
            Indicies.append(Numbers[i])
        
        Xaxis=[]
        Yaxis=[]
        for i in Indicies:
            Xaxis.append(Temp1[i])
            Yaxis.append(Temp2[i])
        plt.scatter(Xaxis, Yaxis, c = color, s = 100)
        if Counter==1:
            LegendList=[OneName]
        if Counter!=1:
            LegendList.append(OneName)
    plt.legend(LegendList, fontsize=20)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    
    
    