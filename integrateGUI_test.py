#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 13:20:48 2019

@author: jy
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from eeg_test import Cortex
import keyboard
import cv2
import numpy as np
import csv
import sys
from datetime import date
import os
import matlab.engine
import time
import shutil
import easygui
from tobii import Tobii
import asyncio
import websocket
import websockets
from Tobii_V1 import calibrate, Start_Streaming
from collections import deque
import g3pylib as g
import multiprocessing

# to prevent eeglab writing all the information in the console, just put debuginformation off code in matlab code. I'll test this out.

def matlab_p(npr,outpt,q, ti):
    #can try by running all functions on same matlab session.
    eng = matlab.engine.start_matlab()
    computed = eng.numpy_test(npr, outpt, nargout=1)
    # npar = np.array(computed)
    print(computed)
    q.put([ti,computed])
    # return npar

async def main():
    #Not using async because instead of asyncio, we are doing multiprocessing.

    
    
    st.title("Emotiv Epoch X for RAS study")
    
    l3,r3 = st.columns([0.5,1])
    with l3:
        eeg = st.checkbox("Emotiv EEG headset")
    with r3:
        tobi = st.checkbox("Tobii Eye Glasses")
    ##def eeg():
    if "run_once" not in st.session_state:
        st.session_state["run_once"] = True
        if os.path.exists("temp"):
            shutil.rmtree("temp")
        os.makedirs("temp")
        st.session_state['eeg_once'],st.session_state['tobi_once'] = True, True
    
    
    
    if eeg and st.session_state['eeg_once']:
        st.session_state['eeg_once'] = False
        url = "wss://localhost:6868"
        user = {
            "license" : "371c5221-95bd-467c-8654-e0ea1ec40f63",
            "client_id":"yIuft9Vwy9FNwn9ZOdVMkuE982fOJGBQzhrjLOsL",
            "client_secret":"XemYxvowff7w5MOqhr8jrUbbPM5A1ntUbOgnqr98FsnHr7NqVvM8d43PrQjckxoaTbBeKzcRbG6V41eX4zNjwEJd3ofhMf8SOmXxT3iXo664BWgUomlIxI3mj20hQ7G8",
            "debit" : 500,
            "number_row_data" : 128*1
        }
        st.session_state["cortex_object"] = Cortex(url, user)
        if not await st.session_state["cortex_object"].grant_access_and_session_info_withoutauthorization():
            st.warning("Please connect the headset first or authorize it again.")
            st.session_state['eeg_once'] = True
        else:
            st.write("headset connected successfully")
    
    if tobi and st.session_state['tobi_once']:
        #CAN PUT A TEST FOR IF TOBII IS CONNECTED OR NOT.
        st.session_state['tobi_once'] = False
        # st.session_state["tobii_object"] = Tobii()
        # if st.session_state["tobii_object"].conn_res:
        #     st.write("Tobii is connected successfully")
        # else:
        #     st.warning("Please ensure the device is connected to Tobii Eye Glasses and try again")
        #     st.session_state['tobi_once'] = True
    
    
    #all the UI components
    
    l1,r1 = st.columns([0.5, 1])
    with l1:
        button1 = st.button("Authorize Emotiv")
    with r1:
        button6 = st.button("Calibrate Tobii")
    student_id = st.text_input("Enter Participant ID", value=1)
    task_number = st.text_input("Enter task number/name", value=1)
    button7 = st.button("Tobii stream")
    l2,r2 = st.columns([0.5,1])
    with l2:
        button2 = st.button("Start recording")
    with r2:
        button3 = st.button("Stop recording")
    path2 = st.text_input("enter file path", value=1)
    button4 = st.button("Load already existing raw data")
    
    #This is only for testing. Can also give filename to print_to_file
    if button7:
        # q = asyncio.Queue()
        # tobii_obj = st.session_state["tobii_object"]
        # await asyncio.gather(tobii_obj.subscribe_to_gaze(q), tobii_obj.print_to_file(q))
        if not os.path.exists("Data/"+str(student_id)+"/"+str(date.today())):
            os.makedirs("Data/"+str(student_id)+"/"+str(date.today()))
        await Start_Streaming("Data/"+str(student_id)+"/"+str(date.today())+"/"+str(task_number)+"_Tobii.csv")
    
    if button6:
        res = await calibrate()
        if res:
            st.write("Calibration was successful")
        else:
            st.write("Calibration failed, try again")
    
    
    
    if button3:
        #put tobii recording stop here.
        async with g.connect_to_glasses.with_url("ws://192.168.75.51/websocket") as g3:
            await g3.recorder.stop()
        st.write("Task recording saved successfully in Desktop/Necromancer/Data/"+str(student_id)+"/"+str(date.today()))
    
    if button1:
        c= st.session_state["cortex_object"]
        res = await c.authorize()
        if res:
            print("authorization is successful.")
            st.write("Authorization is done for the day")
        else:
            print("authorization failed, check internet and emotiv connection")
            st.warning("Authorization has failed, please check your emotiv and internet connection")
    
    
    if button2:
        # task_queue = deque([])
        # tobii_obj = st.session_state["tobii_object"]
        c = st.session_state["cortex_object"]
        q = asyncio.Queue()
        path = "Data/"+str(student_id)+"/"+str(date.today())
        if not os.path.exists(path):
            os.makedirs(path)
    
        #csvfile.flush() everytime after writing it to make it realtime.
        output_path = path+"/"+str(task_number)+"_computed.csv"
        with open(path+"/"+str(task_number)+".csv","a",newline='') as csvfile, open(output_path,"a",newline='') as output_file_temp: 
            writer = csv.writer(csvfile, delimiter=',')
            a=["AF4", "F8", "F4", "FC6", "T8", "P8", "O2", "O1", "P7", "T7", "FC5", "F3", "F7", "AF3",'time']
            writer.writerow(a)
            csvfile.flush()

            # counter = 1
            prevtime = time.time()
            # curfile = open("temp/"+str(counter)+".csv", "a", newline='')
            
            
            #For the header of task_computed file
            output_writer = csv.writer(output_file_temp,delimiter=',')
            channels = ["AF4", "F8", "F4", "FC6", "T8", "P8", "O2", "O1", "P7", "T7", "FC5", "F3", "F7", "AF3"]
            power_means = ["power_means_delta", "power_means_theta", "power_means_alpha", "power_means_beta_low", "power_means_beta_high", "engagement_index"]
            header = []
            for x in power_means:
                for y in channels:
                    header.append(y+"_"+x)

            output_writer.writerow(header)
            output_file_temp.flush()
            output_file_temp.close()
    
            st.write("Recording has started....")
            data = {'x':[str(time.time())], "AF4":[0], "F8":[0], "F4":[0], "FC6":[0], "T8":[0], "P8":[0], "O2":[0], "O1":[0], "P7":[0], "T7":[0], "FC5":[0], "F3":[0], "F7":[0], "AF3":[0]}
            df = pd.DataFrame(data)
            fig = px.line(df, x='x', y=["AF4", "F8", "F4", "FC6", "T8", "P8", "O2", "O1", "P7", "T7", "FC5", "F3", "F7", "AF3"])
            chart = st.plotly_chart(fig)
            eeg_window = []
            async with websockets.connect("wss://localhost:6868") as ws:
                await c.create_session(c.auth,c.headset_id,ws)
                async with g.connect_to_glasses.with_url("ws://192.168.75.51/websocket") as g3:
                    await g3.recorder.start()
                    gaze_queue, unsubscribe_to_gaze = await g3.rudimentary.subscribe_to_gaze()
                    await g3.rudimentary.start_streams()
                    with open("Data/"+str(student_id)+"/"+str(date.today())+"/"+str(task_number)+"_Tobii.csv","a",newline='') as tobii_file:
                        temp_writer = csv.writer(tobii_file,delimiter=',')
                        tobii_header = ["gaze_2d_x","gaze_2d_y", "gaze_3d_x", "gaze_3d_y", "gaze_3d_z","lefteye_pupildiameter", "righteye_pupildiameter"]
                        temp_writer.writerow(tobii_header)
                        mlp_queue = multiprocessing.Queue()
                        
                        while True:
                            await asyncio.sleep(0)

                            if len(eeg_window)>4445:    #so that first sliding window starts after 30 seconds.
                                #update numpy array. -> create task with new numpy array and add it to dequeue using task_queue.append(create_task....)
                                #if task_queue[0].done() then result = await task_queue.popleft() and then print result.
                                # computed = eng.eeglabProcessingcopy(os.path.abspath("temp/"+str(counter)+".csv"), os.path.abspath(output_path), nargout=1)
                                # npar = np.array(computed)
                                eeg_window = eeg_window[-3810:][:]
                                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",len(eeg_window), len(eeg_window[0]))
                                prcs = multiprocessing.Process(target=matlab_p, args=(np.array(eeg_window),os.path.abspath(output_path), mlp_queue, eeg_window[-1][-1]))
                                prcs.start()
                                # task_queue.append(asyncio.create_task(matlab_p(np.array(eeg_window), os.path.abspath(output_path))))
                                if mlp_queue.qsize()>1:
                                    [ti,computed] = mlp_queue.get()
                                    npar = np.array(computed)
                                    print(computed)
                                    # output_writer.writerow(computed)
                                    new_data = pd.DataFrame({'x':[ti], "AF4":[npar[0,-14]], "F8":[npar[0,-13]], "F4":[npar[0,-12]], "FC6":[npar[0,-11]], "T8":[npar[0,-10]], "P8":[npar[0,-9]], "O2":[npar[0,-8]], "O1":[npar[0,-7]], "P7":[npar[0,-6]], "T7":[npar[0,-5]], "FC5":[npar[0,-4]], "F3":[npar[0,-3]], "F7":[npar[0,-2]], "AF3":[npar[0,-1]]})
                                    df = pd.concat([df.tail(9), new_data], ignore_index=True)
                                    for i in range(14):
                                        fig.data[i].x = df['x']
                                        fig.data[i].y = df.iloc[:,i+1]
                                    chart.plotly_chart(fig) 
                            #NEED TO ADD Tobii coroutine here, ADDED but verify first with button7
                            eeg_stream = asyncio.create_task(c.subRequest(ws))
                            tobii_stream = asyncio.create_task(Start_Streaming(gaze_queue, temp_writer))
                            # print(await asyncio.gather(eeg_stream, tobii_stream))
                            [([sensor_data,time_list]),x] = await asyncio.gather(eeg_stream, tobii_stream)
                            # sensor_data,time_list = await c.subRequest(ws)
                            # st.write("len of sensor data is -", len(sensor_data))
                            writer = csv.writer(csvfile, delimiter=',')
                            for i in range (len(sensor_data)):
                                sensor_data[i].append(time_list[i])
                                eeg_window.append(sensor_data[i])
                                writer.writerow(sensor_data[i])
                            csvfile.flush()
                            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$   len of eeg_window -", len(eeg_window))
    
    if button4:
        with open(path2+"/"+str(task_number)+".csv", 'r') as file:
            csvreader = csv.reader(file)
            counter = 1
            prevtime = None
            timeread = None
            curfile = open("temp/"+str(counter)+".csv", "a", newline='')
            # path = "Data/"+str(student_id)+"/"+str(date.today())
            output_path = path2+"/"+str(task_number)+"_computed.csv"
            first_row = next(csvreader)
            for row in csvreader:
    
                timeread = float(row[14])
                if prevtime == None:
                    prevtime = float(row[14])
                if timeread-prevtime>=30:
                    computed = eng.eeglabProcessingcopy(os.path.abspath("temp/"+str(counter)+".csv"), os.path.abspath(output_path), nargout=1)
                    counter += 1
                    curfile.close()
                    prevtime = timeread
                    curfile = open("temp/"+str(counter)+".csv", "a", newline='')
    
    
                windowwriter = csv.writer(curfile, delimiter=',')
                windowwriter.writerow(row)
                file.flush()
        st.write("Processing is completed")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())