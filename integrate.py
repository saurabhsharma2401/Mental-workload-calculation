#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 13:20:48 2019

@author: jy
"""

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
shutil.rmtree('temp')
os.makedirs('temp')

eng = matlab.engine.start_matlab()
##def eeg():
url = "wss://localhost:6868"
user = {
	"license" : "371c5221-95bd-467c-8654-e0ea1ec40f63",
	"client_id":"yIuft9Vwy9FNwn9ZOdVMkuE982fOJGBQzhrjLOsL",
    "client_secret":"XemYxvowff7w5MOqhr8jrUbbPM5A1ntUbOgnqr98FsnHr7NqVvM8d43PrQjckxoaTbBeKzcRbG6V41eX4zNjwEJd3ofhMf8SOmXxT3iXo664BWgUomlIxI3mj20hQ7G8",
	"debit" : 500,
	"number_row_data" : 128*1
}
c = Cortex(url, user)

if len(sys.argv)>1 and sys.argv[1] == "authorize":
	c.authorize()
	print("authorization for the is successful.")
	exit()
student_id = sys.argv[1]
task_number = sys.argv[2]

path = "Data/"+str(student_id)+"/"+str(date.today())

print("Connection successful")
c.grant_access_and_session_info_withoutauthorization()
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

    while True:
        if time.time()-prevtime>=30:
            eng.eeglabProcessing(os.path.abspath("temp/"+str(counter)+".csv"), os.path.abspath(output_path), nargout=0)
            counter += 1
            curfile.close()
            prevtime = time.time()
            curfile = open("temp/"+str(counter)+".csv", "a", newline='')

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