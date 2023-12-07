#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 13:20:48 2019

@author: jy
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from eeg import Cortex
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



st.title("Emotiv Epoch X for RAS study")
eng = matlab.engine.start_matlab()
##def eeg():
if "run_once" not in st.session_state:

	url = "wss://localhost:6868"
	user = {
		"license" : "371c5221-95bd-467c-8654-e0ea1ec40f63",
		"client_id":"yIuft9Vwy9FNwn9ZOdVMkuE982fOJGBQzhrjLOsL",
	    "client_secret":"XemYxvowff7w5MOqhr8jrUbbPM5A1ntUbOgnqr98FsnHr7NqVvM8d43PrQjckxoaTbBeKzcRbG6V41eX4zNjwEJd3ofhMf8SOmXxT3iXo664BWgUomlIxI3mj20hQ7G8",
		"debit" : 500,
		"number_row_data" : 128*1
	}
	st.session_state["cortex_object"] = Cortex(url, user)
	if os.path.exists("temp"):
		shutil.rmtree("temp")
	os.makedirs("temp")
	if not st.session_state["cortex_object"].grant_access_and_session_info_withoutauthorization():
		st.warning("Please connect the headset first")
		st.stop()
	    # if not c.grant_access_and_session_info_withoutauthorization():
    	# st.warning("Please connect the headset first")
    	# st.stop()


c= st.session_state["cortex_object"]
button1 = st.button("Authorize")
student_id = st.text_input("Enter Participant ID", value=1)
task_number = st.text_input("Enter task number/name", value=1)

button2 = st.button("Start recording")
button3 = st.button("Stop recording")
if button3:
    st.write("Task recording saved successfully in Desktop/Necromancer/Data/"+str(student_id)+"/"+str(date.today()))
    st.stop()


path2 = st.text_input("enter file path", value=1)
button4 = st.button("Load already existing raw data")
if button1:
    c.authorize()
    print("authorization for the is successful.")
    st.write("Authorization is done for the day")
    exit()

if button2:
    st.session_state["run_once"] = False
    path = "Data/"+str(student_id)+"/"+str(date.today())

    print("Connection successful")

    print("Also got the information")


    if not os.path.exists(path):
       os.makedirs(path)

    #csvfile.flush() everytime after writing it to make it realtime.

    with open(path+"/"+str(task_number)+".csv","a",newline='') as csvfile: 
        writer = csv.writer(csvfile, delimiter=',')
        a=["AF4", "F8", "F4", "FC6", "T8", "P8", "O2", "O1", "P7", "T7", "FC5", "F3", "F7", "AF3",'time']
        writer.writerow(a)
        csvfile.flush()

        counter = 1
        prevtime = time.time()
        curfile = open("temp/"+str(counter)+".csv", "a", newline='')
        output_path = path+"/"+str(task_number)+"_computed.csv"
        # print(os.path.abspath("temp/"+str(counter)+".csv"))
        # print(os.path.abspath(output_path))

        st.write("Recording has started....")
        data = {'x':[str(time.time())], "AF4":[0], "F8":[0], "F4":[0], "FC6":[0], "T8":[0], "P8":[0], "O2":[0], "O1":[0], "P7":[0], "T7":[0], "FC5":[0], "F3":[0], "F7":[0], "AF3":[0]}
        df = pd.DataFrame(data)
        fig = px.line(df, x='x', y=["AF4", "F8", "F4", "FC6", "T8", "P8", "O2", "O1", "P7", "T7", "FC5", "F3", "F7", "AF3"])
        chart = st.plotly_chart(fig)

        while True:
            if time.time()-prevtime>=30:
                computed = eng.eeglabProcessingcopy(os.path.abspath("temp/"+str(counter)+".csv"), os.path.abspath(output_path), nargout=1)
                # print(type(computed))
                # # print(type(computed.tolist()))
                # print([x for x in computed])
                # print([x[0] for x in computed])
                # print(np.array(computed))
                # print(type(np.array(computed)))
                npar = np.array(computed)
                print(npar)
                counter += 1
                curfile.close()
                prevtime = time.time()
                curfile = open("temp/"+str(counter)+".csv", "a", newline='')
                #plot the graph here
                new_data = pd.DataFrame({'x':[prevtime], "AF4":[npar[0,-14]], "F8":[npar[0,-13]], "F4":[npar[0,-12]], "FC6":[npar[0,-11]], "T8":[npar[0,-10]], "P8":[npar[0,-9]], "O2":[npar[0,-8]], "O1":[npar[0,-7]], "P7":[npar[0,-6]], "T7":[npar[0,-5]], "FC5":[npar[0,-4]], "F3":[npar[0,-3]], "F7":[npar[0,-2]], "AF3":[npar[0,-1]]})
                df = pd.concat([df.tail(9), new_data], ignore_index=True)

                for i in range(14):
                    fig.data[i].x = df['x']
                    fig.data[i].y = df.iloc[:,i+1]
                chart.plotly_chart(fig)

    	    # need disconnect headset befor export
            sensor_data,time_list = c.subRequest()
    	    # print(sensor_data[1])
    	    # with open(path,"a+",newline='') as csvfile: 
            writer = csv.writer(csvfile, delimiter=',')
            windowwriter = csv.writer(curfile, delimiter=',')
            for i in range (len(sensor_data)):
                windowwriter.writerow(sensor_data[i])
                sensor_data[i].append(time_list[i])
                writer.writerow(sensor_data[i])
            curfile.flush()
            csvfile.flush()

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

    	    # print(sensor_data[1])
    	    # with open(path,"a+",newline='') as csvfile: 
            windowwriter = csv.writer(curfile, delimiter=',')
            windowwriter.writerow(row)
            file.flush()
    st.write("Processing is completed")