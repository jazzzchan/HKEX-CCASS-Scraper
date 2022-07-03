#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 12:23:22 2022

@author: jessiechen
"""

#https://pysimplegui.readthedocs.io/en/latest/cookbook/
#https://www.programcreek.com/python/example/116003/PySimpleGUI.Column



import json, os, time
import PySimpleGUI as sg
from datetime import datetime,date,timedelta
import threading, random
import pandas as pd
from tkinter import filedialog
import function

sg.theme("LightBlue")
sg.set_options(
    font=('Arial',12),
    background_color='white',
    text_color='black'
)

days2 = timedelta(days=1)
today = datetime.today().date()

eve = threading.Event()


def run():
    '''main program and GUI loop
    '''
    a = sg.Column([[sg.T('Start Date*')],[sg.InputText(str(today-days2),size=(10,2), background_color='white',border_width=1,tooltip="格式：xxxx-xx-xx ",key="startdate",enable_events=True)]])
    b = sg.Column([[sg.T('End Date*')],[sg.InputText(str(today-days2),size=(10,2), background_color='white',border_width=1,tooltip="格式：xxxx-xx-xx ",key="enddate",enable_events=True)]])
    c = sg.Column([[sg.T('Stock Code*')],[sg.InputText('',size=(10,2), background_color='white',border_width=1,tooltip="eg：00001",key="stockcode",enable_events=True)]])
    d = sg.Column([[sg.T('Threshold % of total number of shares\n(for transaction finder)')],[sg.InputText('',size=(10,2), background_color='white',border_width=1,key="threshold percentage",enable_events=True), sg.T('%')]])

    table =sg.Column(
        [
            [sg.Table(
                values=[['','','','','','']],
                headings=['Date','Participant ID','Participant Name', 'Address', 'Shareholding', 'Threshold % of Total'],
                col_widths=[15,15,30,30,15,15],
                display_row_numbers=True,
                background_color='white',
                text_color='black',
                expand_x=True,
                num_rows=20,
                justification='center',
                expand_y=True,
                font=("",10),
                key='table',
                auto_size_columns=False,
                header_background_color="#80ffff",
                select_mode=sg.SELECT_MODE_BROWSE,
                bind_return_key=True,
                pad=((2, 2),(1,1))
    )]
            ]
    )


    layout = [
        [a,b],
        [c],
        [d],
        [sg.Button("trend plot", key="start"),
         sg.Button('tansaction finder',key="sort"),
         sg.Button('Show Top10',key='top10',tooltip='The top10 data are shown from the source of orginal data'),
         sg.Button('Export Data',key='export'),
         sg.T('',key='show', background_color='white')],
        [table],
        [sg.Button('clear all',key='clear')],
    ]

    window = sg.Window(title="CCASS Shareholding Search",layout=layout, finalize=True)

    stop = True
    show = False
    df = None

    while True:
        event, value = window.read()
        if event == "export":
            if df is None:
                window['show'].update('Please get data first')
                continue
            try:
                window['show'].update('')
                time.sleep(1)
                path = filedialog.asksaveasfilename(initialdir='./', filetypes=(('EXCEL', '*.xlsx'),))
                df.to_excel(path, engine='openpyxl')
                window['show'].update('Export data success')
            except:
                pass

        if event == 'sort':
            if value['threshold percentage'] == '':
                sg.Popup('Please input the threshold percentage', auto_close=True, auto_close_duration=2)
                continue

            if df is None:
                sg.Popup('Please click the [trend plot] button to get the data first ', auto_close=True, auto_close_duration=2)
                continue
            df = df_original[df_original['Threshold % of Total']>float(value['threshold percentage'])]
            table_value = [i for i in df.values.tolist()]
            window['table'].update(values=table_value)
            window['show'].update('Data is sorted')

        if event == 'top10':
            if df is None:
                sg.Popup('Please click the [trend plot] button to get the data first ', auto_close=True,
                         auto_close_duration=2)
                continue

            show = not show

            if show:
                df = df_original.sort_values(by=['Threshold % of Total'], ascending=False)
                df = df.head(10)
                table_value = [i for i in df.values.tolist()]
                window['table'].update(values=table_value)
                window['show'].update('Top10 datas are selected according to Threshold % of Total')
                window['top10'].update('Show Original')
            else:
                df = df_original
                table_value = [i for i in df.values.tolist()]
                window['table'].update(values=table_value)
                window['show'].update('Original datas are selected')
                window['top10'].update('Show Top10')

        if event == 'clear':
            window['show'].update(value='')
            window['table'].update(values=[[]])
            df = None

        if event == "start":
            if value['startdate'] != '' and value['enddate'] != '' and value['stockcode'] != '':
                stop = not stop
                if not stop:
                    window['start'].update("stop")
                    f = function.Function(window, value)
                    t_start = threading.Thread(target=f.run)
                    t_start.start()
                elif stop:
                    pass
                    # window['start'].update("trend plot")
            else:
                sg.popup("please fill up the necessary content")

        if event == 'result':
            stop = True
            window['start'].update('trend plot')
            if value['result'] == []:
                window['show'].update('No data qulifiled')
            df = pd.DataFrame(value['result'], columns=['Date','Participant ID','Participant Name', 'Address', 'Shareholding', 'Threshold % of Total'])
            df['Shareholding'] = df['Shareholding'].astype(dtype='float')
            df['Threshold % of Total'] = df['Threshold % of Total'].astype(dtype='float')
            df_original = df.copy()
            table_value = [i for i in df.values.tolist()]
            window['table'].update(values=table_value)

#        if event == "message":
#            window['show'].update(value['message'])


        if event in [None, "quit"]:
            break

    window.close()




if __name__ == '__main__':
    run()
