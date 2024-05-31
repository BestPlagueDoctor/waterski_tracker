#  Skier's Helpful Information Tracker
## ECE 445 Senior Design Project

## Authored by Sam Knight and Ryder Heit
This software is the python3 implementation of the processing subsystem of our senior design project. In the ./final folder you can find the finished product scripts read_data.py, tk.py, and ski_functions.py. read_data.py prompts the user and reads data from a .CSV file containing skiing data. tk.py runs the tkinter visualization tool for the output ski data from read_data.py. ski_functions merely contains the functions used by read_data.py. The ./gui and ./maps folders contain various development snippets and versions of the software as it was being written in jupyter notebooks.

To run the python3 tools, the following libraries are required. scipy, numpy, matplotlib, PIL cv2, requests, tkinter, sys, re, os, csv, tqdm. The following system-wide tools are also required to run the tool: FFMpeg, opencv, tkinter. Any python3 package manager that respects [PEP 621](https://www.python.org/dev/peps/pep-0621) can take advantage of the included pyproject.toml to resolve dependency versions as used by the author. Additionally, a flake.nix is provided for use with the nix package management system for dependency installs.
