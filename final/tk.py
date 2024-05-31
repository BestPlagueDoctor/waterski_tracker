import os
import tkinter as tk
from tkinter import filedialog
from tkVideoPlayer import TkinterVideo
import matplotlib.pyplot as plt
import numpy as np
import datetime


# updates the duration after finding it from the video file
def update_duration(event):
    duration = map_player.video_info()["duration"]
    end_time["text"] = str(datetime.timedelta(seconds=duration))
    progress_slider["to"] = duration


def update_scale(event):
    """ updates the scale value and syncs vids """
    progress_value.set(map_player.current_duration())


def load_video():
    """ loads the video """
    dir_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select output directory with ski videos")
    mapfile = dir_path + "/map.mp4"
    pitch_yaw_roll_file = dir_path + "/pitch_yaw_roll.mp4"
    speed_file = dir_path + "/speed.mp4"
    map_player.load(mapfile)
    speed_player.load(speed_file)
    pitch_yaw_roll_player.load(pitch_yaw_roll_file)

    progress_slider.config(to=0, from_=0)
    playpause_btn["text"] = "Play"
    progress_value.set(0)

def seek(value):
    """ used to seek a specific timeframe """
    for vid_player in vid_players:
        vid_player.seek(int(value))

def skip(value: int):
    """ skip seconds """
    progress_value.set(progress_slider.get() + value)
    for vid_player in vid_players:
        vid_player.seek(int(progress_slider.get()))

def play_pause():
    """ pauses and plays """
    for vid_player in vid_players:
        if vid_player.is_paused():
            vid_player.play()
            playpause_btn["text"] = "Pause"

        else:
            vid_player.pause()
            playpause_btn["text"] = "Play"
        
def video_ended(event):
    """ handle video ended """
    progress_slider.set(progress_slider["to"])
    playpause_btn["text"] = "Play"
    progress_slider.set(0)
    #map_player.seek(0)
    #speed_player.seek(0)
    #pitch_yaw_roll_player.seek(0)
    #map_player.pause()
    #speed_player.pause()
    #pitch_yaw_roll_player.pause()


# make root and start setting up window
root = tk.Tk()
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1920-960)
root.grid_columnconfigure(1, weight=960)
root.title("Ski Visualization 9000")
root.geometry("1920x1080")  # set starting size of window

# make frames to put objects into for organization
map_frame = tk.Frame(root, width=1920-960, height=1080-20)
video_controls = tk.Frame(root, width=1920, height=10)
seek_bar = tk.Frame(root, width=1920, height=10)
graph_frame = tk.Frame(root, width=960, height=(1080-20))

# assign weights so they'll stretch
map_frame.grid_rowconfigure(1, weight=1)
map_frame.grid_columnconfigure(0, weight=1)
video_controls.grid_rowconfigure(0, weight=1)
video_controls.grid_columnconfigure(0, weight=1)
video_controls.grid_columnconfigure(1, weight=1)
seek_bar.grid_rowconfigure(0, weight=1)
seek_bar.grid_columnconfigure(2, weight=1)
graph_frame.grid_rowconfigure(1, weight=1)
graph_frame.grid_rowconfigure(3, weight=1)
#graph_frame.grid_rowconfigure(5, weight=1)
#graph_frame.grid_rowconfigure(7, weight=1)
graph_frame.grid_columnconfigure(0, weight=1)

# grid frames into main window
map_frame.grid(row=0, column=0, sticky="news")
graph_frame.grid(row=0, column=1, sticky="news")
video_controls.grid(row=1, column=0, sticky="ew", columnspan=2)
seek_bar.grid(row=2, column=0, sticky="ew", columnspan=2)

# make objects
load_btn = tk.Button(video_controls, text="load video", command=load_video)
playpause_btn = tk.Button(video_controls, text="Play/Pause",command=play_pause)
skip_plus_5 = tk.Button(seek_bar, text="+1s", command=lambda:skip(1))
skip_minus_5 = tk.Button(seek_bar, text="-1s", command=lambda:skip(-1))
start_time = tk.Label(seek_bar, text=str(datetime.timedelta(seconds=0)))
progress_value = tk.IntVar(seek_bar)
progress_slider = tk.Scale(seek_bar, variable=progress_value, from_=0, to=0, orient="horizontal", command=seek)
end_time = tk.Label(seek_bar, text=str(datetime.timedelta(seconds=0)))

# grid em in
load_btn.grid(row=0, column=0, sticky="e")
playpause_btn.grid(row=0, column=1, sticky="w")
skip_plus_5.grid(row=0, column=3, sticky="w")
start_time.grid(row=0, column=1,sticky="w")
progress_slider.grid(row=0, column=2, sticky="news")
skip_minus_5.grid(row=0, column=0,sticky="e")
end_time.grid(row=0, column=4,sticky="e")

# Create labels
map_label = tk.Label(map_frame, text="Live Map")
speed_label = tk.Label(graph_frame, text="Speed")
pitch_label = tk.Label(graph_frame, text="Pitch")
#yaw_label = tk.Label(graph_frame, text="Yaw")
#roll_label = tk.Label(graph_frame, text="Roll")

# grid em in
map_label.grid(row=0,column=0)
speed_label.grid(row=0,column=0)
pitch_label.grid(row=2,column=0)
#yaw_label.grid(row=4,column=0)
#roll_label.grid(row=6,column=0)

# the players
# i will assign one thread per video player, and call each gui function on each thread. will it work?
vid_players = []
map_player = TkinterVideo(master=map_frame)
map_player.set_size((960,960))
map_player.grid(row=1, column=0, sticky="news")
vid_players.append(map_player)
speed_player = TkinterVideo(master=graph_frame)
speed_player.set_size((960, 480))
speed_player.grid(row=1, column=0, sticky="news")
vid_players.append(speed_player)
pitch_yaw_roll_player = TkinterVideo(master=graph_frame)
pitch_yaw_roll_player.set_size((960, 480))
pitch_yaw_roll_player.grid(row=3, column=0, sticky="news")
vid_players.append(pitch_yaw_roll_player)
#yaw_player = TkinterVideo(master=graph_frame)
#yaw_player.set_size((1280, 465))
#yaw_player.grid(row=5, column=0, sticky="news")
#vid_players.append(yaw_player)
#roll_player = TkinterVideo(master=graph_frame)
#roll_player.set_size((1280, 465))
#roll_player.grid(row=7, column=0, sticky="news")
#vid_players.append(roll_player)
# we can bind these events to only one of the video players because I'm the one making the videos, and i can pinky promise they'll all be the same length. sound good?
map_player.bind("<<Duration>>", update_duration)
map_player.bind("<<SecondChanged>>", update_scale)
map_player.bind("<<Ended>>", video_ended)

root.mainloop()
