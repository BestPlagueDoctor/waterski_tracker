#  Data Extraction and Processing for ECE 445 Senior Design
#
#  Code written by Sam Knight for Skier's Helpful Information Tracker
#  Project Team 52, sknight5, ryderch2, jackb3
#
#  This program extracts data from the ski tracker's CSV containing
#  gps, speed, direction, time, and other stats and creates a 
#  visualization of the map as well as the data as it changes over
#  time. The bundled tk.py is available to visualize the results of 
#  this code. 
#
#  Required libraries (python and otherwise): scipy, numpy, matplotlib, PIL
#  cv2, requests, tkinter, sys, re, os, csv, tqdm. Required software: 
#  FFMpeg, opencv, tkinter
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of I don't care what you do with it
#  as published by me, Sam Knight.
#  
#  Many thanks to the various stack posts that helped me write all 
#  of the GPS math.

# imports
# python basics
import os
import re
import sys
import csv
import subprocess
from pathlib import Path

# math helpers
from scipy.signal import medfilt
from scipy.interpolate import Akima1DInterpolator
import numpy as np
import matplotlib.pyplot as plt

# image processing, web tools, niceties
import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
from matplotlib import animation
from PIL import Image, ImageOps, ImageDraw
from tqdm import tqdm

# function defs
from ski_functions import *

""" Globals and why
zoom: the zoom level of the map as requested by the API. set to where a\
        slalom course fills about the center %40 of the image.
scale: upscaling option provided by google api. allows us to grow our image\
        beyond the maximum size of 640x640.
w, h: the desired w, h of the maps image. relative x/y math depends on the w,h\
        of the desired maps image, so it's good to just have it as a global.
"""
zoom = 17
scale = 2
w, h = 960, 960


# prompt user for data they want to use
root = tk.Tk()
root.withdraw()
# if the data dir doesn't exist, make it (just in case...)
Path("./data").mkdir(parents=True, exist_ok=True)
data_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select ski data to process", filetypes=[("csv datasets", "*.csv"), ("csv datasets", "*.CSV")], multiple=False)
if data_path:
    print(data_path)
    if data_path[-4:] != ".csv" or data_path[-4:] != ".CSV":
        print("disabled this check for now")
        #sys.exit("ERROR: selected a non-csv file. please try again")
    out_dir = "output_" + data_path[-10:-4]
    print(out_dir)
    try:
        Path("./" + out_dir).mkdir(parents=True, exist_ok=False)
        print("Writing data to " + out_dir)
    except FileExistsError:
#        print("haha")
        sys.exit("ERROR: data has already been processed! if you believe this is an error or have updated the data manually, remove output directory " + out_dir + " and try again.")

else:
    sys.exit("ERROR: data path was empty. please supply correct path to ski data")

# get number of lines to init np arrays
if data_path:
    with open(data_path, 'r') as fp:
        numlines = len(fp.readlines()) - 1
else:
    sys.exit("ERROR: data path was empty. please supply correct path to ski data")

# init np arrays
timescale = np.zeros(numlines, dtype=np.float64)
lat = np.zeros(numlines)
lon = np.zeros(numlines)
lat_s = np.zeros(numlines)
lon_s = np.zeros(numlines)
coords = np.empty(numlines, dtype=object)
pitch = np.zeros(numlines)
yaw = np.zeros(numlines)
roll = np.zeros(numlines)
speed = np.empty(numlines)

# populate np arrays
i = 0
if data_path:
    with open(data_path, 'r') as file:
        data = csv.DictReader(file, delimiter=',')
        for line in data:
            timescale[i] = float(line["ms"])
            lat[i] = float(line["lat"])
            lon[i] = float(line["lon"])
            coords[i] = (float(line["lat"]), float(line["lon"]))
            pitch[i] = float(line["pitch"])
            yaw[i] = float(line["yaw"])
            roll[i] = float(line["roll"])
            i += 1
# shouldn't make it here, we should fail earlier. just a redundancy check
else:
    sys.exit("ERROR: data path was empty. please supply correct path to ski data")

# smooth our noisy data!
lat_s = filter_(lat)
lon_s = filter_(lon)
for i in range(numlines):
    coords[i] = (lat_s[i], lon_s[i])

for i in range(len(coords)-1):
    speed[i] = float(gps_dist(coords[i+1], coords[i]) / (0.1))

"""
N = 35
window = np.hamming(N)/sum(np.hamming(N))
pitch = np.convolve(pitch, window, mode='same').tolist()
yaw = np.convolve(yaw, window, mode='same').tolist()
roll = np.convolve(roll, window, mode='same').tolist()
N3 = 5
speed = medfilt(speed, N3)
N2 = 21
beta = 5
window2 = np.kaiser(N2, beta)/sum(np.kaiser(N2, beta))
speed = np.convolve(speed, window2, mode='same').tolist()
"""

center = ((coords[0][0] + coords[-1][0])/2.0, (coords[0][1] + coords[-1][1])/2.0)
map_ = get_map(coords[0], coords[-1])

# animate map
map_imgs = []
width, height = 960, 960
print("Fetching image data from maps")
for i in tqdm(range(2,numlines-1)):
    im = get_map(coords[0], coords[-1])
    im_path = draw_skier_path(im, coords, center)
    im_balls = draw_balls(im_path, coords[0], coords[-1], center)
    skierpos =  ((coords[i+1][0] + coords[i][0])/2.0, (coords[i+1][1] + coords[i][1])/2.0)
    im_skier = draw_skier(im_balls, skierpos, center)
    map_imgs.append(im_skier)
#map_imgs[0].save('map.gif', save_all=True, append_images=map_imgs[1:], optimize=False, duration=int(timescale[1]-timescale[0]))


#TODO write images using opencv
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter('./' + out_dir + '/map.mp4', fourcc, 10, (960, 960))
print("Processing image data")
for frame in tqdm(map_imgs[:-10]): 
    frame = frame.convert("RGB")
    cv_frame = np.array(frame)
    cv_frame = cv2.resize(cv_frame, (960, 960))
    cv_frame = cv2.cvtColor(cv_frame, cv2.COLOR_RGB2BGR)
    video.write(cv_frame)
video.release()

# animate stats
ffwriter = animation.FFMpegWriter(fps=10, extra_args=['-vcodec', 'libx264', '-x264-params', 'keyint=1:scenecut=0'])
fig, ax = plt.subplots(figsize=(960//96, 520//96))
xdata, ydata0, ydata1, ydata2 = [], [], [], []
pitch_line, = plt.plot([], [], 'r', animated=True)
yaw_line, = plt.plot([], [], 'g', animated=True)
roll_line, = plt.plot([], [], 'b', animated=True)
np_time = np.linspace(timescale[0], timescale[-1], len(timescale))
labels = ["pitch", "yaw", "roll"]
leg = plt.legend(labels, loc="upper right")
plt.title("Pitch Yaw and Roll of Ski")
plt.xlabel("Seconds")
plt.ylabel("Degrees of Change")


def init_pyw():
    ax.set_xlim(0, timescale[-1]//1000)
    ax.set_ylim(-90, 90)
    pitch_line.set_data(xdata, ydata0)
    yaw_line.set_data(xdata, ydata1)
    roll_line.set_data(xdata, ydata2)
    return pitch_line, yaw_line, roll_line    

def update_pyw(frame):
    idx = int(frame*10)
    xdata.append(frame)    
    ydata0.append(pitch[idx])
    ydata1.append(yaw[idx])
    ydata2.append(roll[idx])
    pitch_line.set_data(xdata, ydata0)
    yaw_line.set_data(xdata, ydata1)
    roll_line.set_data(xdata, ydata2)
    return pitch_line, yaw_line, roll_line,

print("Processing gryo data")
ani_pyw = animation.FuncAnimation(fig, update_pyw, frames=tqdm(np_time[:-5]/1000, file=sys.stdout), init_func=init_pyw, blit=True, repeat=False)
ani_pyw.save('./' + out_dir + '/pitch_yaw_roll.mp4', dpi=96, writer=ffwriter)

fig1, ax1 = plt.subplots(figsize=(960//96, 520//96))
xdata, ydata0, ydata1 = [], [], []
speed_line, = plt.plot([], [], 'r', animated=True)
fake_line, = plt.plot([], [], 'b', animated=True)
labels = ["speed"]
leg = plt.legend(labels, loc="upper right")
plt.title("Skier Speed")
plt.xlabel("Seconds")
plt.ylabel("Speed m/s")

def init_speed():
    ax1.set_xlim(0, timescale[-1]//1000)
    ax1.set_ylim(0, 20)
    speed_line.set_data(xdata, ydata0)
    fake_line.set_data(xdata, ydata1)
    return speed_line, fake_line

def update_speed(frame):
    idx = int(frame*10)
    xdata.append(frame)
    ydata0.append(speed[idx])
    speed_line.set_data(xdata, ydata0)
    return speed_line, fake_line,

print("Processing speed data")
ani_speed = animation.FuncAnimation(fig1, update_speed, frames=tqdm(np_time[:-5]/1000, file=sys.stdout), init_func=init_speed, blit=True, repeat=False)
ani_speed.save('./' + out_dir + '/speed.mp4', dpi=96, writer=ffwriter)
print("Success! Output data is written to: " + out_dir)

res = mb.askquestion('Run Visualization?', "Would you like to open the visualization now?")
if res == 'yes':
    subprocess.Popen(['python3', 'tk.py'])
    root.destroy()
    sys.exit()
else:
    mb.showinfo('Exit', "Okay! You can always launch the visualization using the file tk.py. Bye!")
    root.destroy()
    sys.exit()
