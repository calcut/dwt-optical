# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:36:18 2022

@author: jrsperling
"""
import PySimpleGUI as sg
import time
from MainCodeAsFunction_17_06_22 import analyse_datasets

def runningDisplay():
    window['-UPDATE-'].update(visible=True)
    window['Run'].update(disabled=True)
    window['Cancel'].update(disabled=True)
    #print('display')

sg.theme('DarkBlue3')   # Add a touch of color
# All the stuff inside your window.
layout1 = [  [sg.Text('This functionality will allow you to analyse SpectraWiz and Optosky data.',font=(20))],
            [sg.Text('Folder'), sg.In(key='-FOLDER-'), sg.FolderBrowse(target='-FOLDER-')],
            [sg.Text('Which type of data is to be analysed:')], 
            [sg.Radio('SpectraWiz     ', "DType", key='SpectraWiz', default=True), sg.Radio('Optosky', "DType", key='Optosky')],
            [sg.Text('Should the code look for mimina or maxima?')], 
            [sg.Radio('Minima     ', "PType", key='Min', default=True), sg.Radio('Maximum', "PType", key='Max')],
            [sg.Text('Define the range of the data:')],
            [sg.Slider(range=(400, 975), orientation='h', size=(75, 20), resolution=25, default_value=400, key='WMin', enable_events = True)],
            [sg.Slider(range=(425, 1000), orientation='h', size=(75, 20), resolution=25, default_value=900, key='WMax', enable_events = True)],
            [sg.Checkbox('Smooth Data', key='Smooth', default=True),sg.Slider(range=(2, 10), orientation='h', size=(20, 20), resolution=1, default_value=3, key='SmoothPoints', enable_events = True), sg.Text('Points to Smooth')],
            [sg.Checkbox('Interpolate Data', key='Interpolate', default=False),sg.Slider(range=(.1, 1), orientation='h', size=(20, 20), resolution=.1, default_value=.3, key='SamplingRate', enable_events = True), sg.Text('Points to Interpolate')],
            [sg.Checkbox('Normalise Data', key='Normalise', default=False)],
            [sg.Text('')],
            [sg.Text('Plotting Options:',font=(20))],
            [sg.Checkbox('Turn on graphing', key='AllGraphs', default=True),
             sg.Checkbox('Plot all on same axes', key='AllPlot', default=True),
             sg.Checkbox('Show Minima on graph', key='ShowMinimaLine', default=True)],
            [sg.Text('                              '),
             sg.Checkbox('Overlay sensors', key='OverlaySensors', default=False),
             sg.Checkbox('Overlay samples', key='OverlaySamples', default=False),],
            [sg.Text('Analysis/Outputs:',font=(20))],
            [sg.Checkbox('Output smoothed, averaged data into CSV file', key='OutputSmoothedCSVFile', default=True),
             sg.Checkbox('Try running PCA', key='Do_PCA_Q', default=False)],
            [sg.Text('Processing data: Please do NOT close this window...',font=(20), key='-UPDATE-',visible=False)],
            [sg.Button(button_text='Run',initial_folder=''), sg.Button('Cancel')]
          ]

layout2 = [ [sg.Text('Analysis Complete!\nPress close to generate plots\nTo process a new set of data,\nyou will need to run the software again.',font=(40))],
            #[sg.Text('Press close to generate plots.',font=(40))],
            #[sg.Text('To process a new set of data,',font=(40))],
            #[sg.Text('you will need to run the software again!',font=(40))],
            [sg.Button('Close')]
          ]

layout = [
            [sg.Column(layout1, key='-COL1-'),  
             sg.Column(layout2, visible=False, key='-COL2-')
            ]
         ]

# Create the Window
window = sg.Window('SpectraAnalysis', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel' or event == 'Close': # if user closes window or clicks cancel
        break
    #print('You entered ', str(values[0]))
    if event == '-FOLDER-':
        folder = values['-FOLDER-']  
    elif event == 'WMin':
        if values['WMin'] >= values['WMax']:
            value_min = values['WMin']
            window['WMax'].update(value=value_min+25)
    elif event == 'WMax':
        if values['WMin'] >= values['WMax']:
            value_max = values['WMax']
            window['WMin'].update(value=value_max-25)
   
    
    elif event == 'Run':
        #runningDisplay()
        window['-UPDATE-'].update(visible=True)
        window['Run'].update(disabled=True)
        window['Cancel'].update(disabled=True)
        #window['-COL2-'].update(visible=True)
        #print('running')
        
            
        time.sleep(2)
        folder = values['-FOLDER-']
        
        DataSet=folder
        
        SpectraWiz_Select = values['SpectraWiz']
        OptoSky_Select = values['Optosky']
        
        if values['Max']:
            TypeM = 'Max'
        else:
            TypeM = 'Min'
        
        WMin = values['WMin']
        WMax = values['WMax']
        
        Smooth = values['Smooth']
        SmoothPoints = values['SmoothPoints']
        
        Interpolate = values['Interpolate']
        SamplingRate = values['SamplingRate'] 
        Normalise = values['Normalise']
        
        # Choose overlaying plots
        
        OverlaySensors = values['OverlaySensors']
        OverlaySamples = values['OverlaySamples']
        AllPlot = values['AllPlot']
        ShowMinimaLine = values['ShowMinimaLine']
        
        # Turn off all graphs plotting with minima and errors attached
        AllGraphs = values['AllGraphs']
        
        Do_PCA_Q = values['Do_PCA_Q']
        
        OutputSmoothedCSVFile = values['OutputSmoothedCSVFile']
        
        finish = analyse_datasets(DataSet,SpectraWiz_Select,OptoSky_Select,TypeM,WMin,WMax,Smooth,SmoothPoints,
                        Interpolate,SamplingRate,Normalise,OverlaySensors,OverlaySamples,AllPlot, AllGraphs,
                        ShowMinimaLine,Do_PCA_Q,OutputSmoothedCSVFile)
        if finish == 1:
            window['-COL1-'].update(visible=False)
            window['-UPDATE-'].update(visible=False)
            window['-COL2-'].update(visible=True)
        
window.close()

