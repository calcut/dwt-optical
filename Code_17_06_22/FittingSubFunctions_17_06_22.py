# -*- coding: utf-8 -*-
"""
Created on Mon May 24 15:17:29 2021

@author: IainC
"""

# Fitting Sub Functions
   
def Reframe(Wav,Trans):
    
    # This code determines which side of the curve is higher
    # and cuts this part of the curve in order to have an even 
    # curve for fitting.
    
    MinimaAreaT_N=[]
    MinimaAreaW_N=[]
    THalf1=Trans[0:(len(Wav)//2)]
    Half1M=max(THalf1)
    THalf2=Trans[(len(Wav)//2):len(Wav)];
    Half2M=max(THalf2)
    # For when the 2nd half is higher than the 1st
    if Half2M>Half1M:
        for i in range(len(THalf2)):
            Val=THalf2[i]
            if Val>=Half1M:
                T=THalf2[0:i]
                MinimaAreaT_N=THalf1+T
                MinimaAreaW_N=Wav[0:len(MinimaAreaT_N)]
                break
    # For when  1st half higher than second
    if Half1M>Half2M:
       for i in range(len(THalf1)):
            Val=THalf1[i]
            if Val<=Half2M:
                T=THalf1[i:len(THalf1)]
                MinimaAreaT_N=T+THalf2
                MinimaAreaW_N=Wav[i:len(Wav)]
                break
    # On the off chance they are equal
    if Half1M==Half2M:
        MinimaAreaT_N=Trans
        MinimaAreaW_N=Wav
    
    return MinimaAreaT_N,MinimaAreaW_N


def FindInflections(DiffVals,Wav,Trans):
    
    InflectionStore=[]
    IFTransStore=[]
    Above=0
    Below=0
    for i in range(len(DiffVals)):
        Val=DiffVals[i]
        if Val>0:
            Above=1
            if Below==1 and Above==1:
                IFTransStore.append(Trans[i])
                InflectionStore.append(Wav[i])
            Below=0
        if Val<0:
            Below=1
            if Below==1 and Above==1:
                IFTransStore.append(Trans[i])
                InflectionStore.append(Wav[i])
            Above=0
            
    return(InflectionStore,IFTransStore)
            
            


