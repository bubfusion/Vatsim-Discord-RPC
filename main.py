from pypresence import Presence
import requests
import tkinter as tk
import customtkinter as ctk
import os
import sys
import configparser
from datetime import datetime, timezone
from update import check_for_update
from CTkMessagebox import CTkMessagebox
import webbrowser
import logging
from logging.handlers import RotatingFileHandler
import vatsim_api
import logging_setup

# pyinstaller main.py --onefile --icon=VATSIM.ico --add-data "VATSIM.ico;." -w -n Vatsim-Discord-RPC
version = "v1.0.2"
up_to_date = check_for_update(version=version)
log = logging_setup.setup_logging()

'''Used for VATSIM.ico file during compiling'''
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Path for config.ini
roaming_path = os.path.join(os.getenv('APPDATA'), "VATSIM-Discord-RPC")

# If path does not exist, then creates it
if not os.path.exists(roaming_path):
    os.makedirs(roaming_path)

# Stores path for config file
ini_file_path = os.path.join(roaming_path, 'config.ini')


# If the config file does not exist, creates it with needed info
if not os.path.exists(ini_file_path):
    with open(ini_file_path, 'w') as ini_file:
        ini_file.write('[Settings]\n')
        ini_file.write('cid=\n')

# Config parser for reading and writing
config = configparser.ConfigParser()
config.read(ini_file_path)



# Discord dev client id
client_id = "1344534564244160662"
RPC = Presence(client_id)

# UI setup
root = ctk.CTk()
root.title("VATSIM Discord Rich Presence")
root.geometry("450x200")
root.wm_iconbitmap(resource_path("VATSIM.ico"))
if up_to_date == False:
  msg = CTkMessagebox(title="Out of date client", message="There is an update available!", 
                option_1="Close", option_2="Download")
  print(msg)
  if msg.get() == "Download":
    webbrowser.open("https://github.com/bubfusion/Vatsim-Discord-RPC/releases")

# cid and checkbox values
cid_var = tk.StringVar()
checkbox_var = ctk.BooleanVar(value=False)
cid = 0

'''Runs after clicking submit. Obtains and updates RPC data and .ini if needed'''
def submit():
  global cid 
  try:
    cid = int(cid_var.get())
    if checkbox.get():
      config.set("Settings", "cid", str(cid))
      with open(ini_file_path, "w") as config_file:
        config.write(config_file)

    update_presence()
  except:
    status_label.configure(text="Invalid CID!")


# Checkbox for making cid default
checkbox = ctk.CTkCheckBox(
    root,
    text="Make default",
    variable=checkbox_var,
    onvalue=True,
    offvalue=False,
)


# CID entry area
cid_label = ctk.CTkLabel(root, text = 'CID', font=('arial ',10, 'bold'))
cid_entry = ctk.CTkEntry(root,textvariable = cid_var, font=('arial ',10,'normal'))

# Submit button
sub_btn= ctk.CTkButton(root,text = 'Submit', command = submit)

# Adds elements to window
cid_label.pack(anchor="center")
cid_entry.pack(anchor="center")
checkbox.pack(pady=20)

sub_btn.pack(anchor="center")

# Default text when RPC is not connected
status_label = ctk.CTkLabel(root, text="Please open discord")
status_label.pack(anchor='center')


def connect_to_discord():
  # Trys to connect to discord, and catches it if fails (such as discord not being opened)
  try:
    RPC.connect()
    status_label.configure(text="RPC connected. Waiting for CID...")
    # Sets cid from config.ini if it exists
    if config.get("Settings", "cid") != "" and config.get("Settings", "cid") != None:
      global cid
      cid = int(config.get("Settings", "cid"))
      cid_entry.insert(0,str(cid))
      # Updates based on default cid if it is entered
      update_presence()
      log.info("Default CID found and discord updated")
  # Runs if RPC wrapper can't make connection with discord
  except Exception as e:
    log.warning(e)
    status_label.configure(text="Please open discord")
    # Checks connection again after 5 seconds
    root.after(5000, connect_to_discord)


'''Updates UI and discord RPC to display flight details'''
def update_presence():

  # If user is invalid
  if (vatsim_api.valid_cid(cid) == False):
    status_label.configure(text=f"CID: {cid} is invalid")
    RPC.clear(1)

  else:
    data = vatsim_api.get_data(cid)

    # If user is offline
    if (data == None):
      status_label.configure(text=f"{cid} is offline")
      # Clears message
      RPC.clear(1)
    else:
      
      formated_string = ""

      # Sets depature airport
      if data[1]:
        formated_string += f"{data[1]}"
      # Sets arrival airport
      if data[2]:
        formated_string += f"➜{data[2]} | "
      # If no arrival airport, but has depature
      elif data[1]:
        formated_string += f" | "
      # Sets callsign
      if data[0]:
        formated_string += f"Callsign: {data[0]} | "
      # Sets flight rules
      if data[4]:
        formated_string += f"{data[4]} | "
      # Sets altitude
      if data[3]:
        formated_string += f"Alt: {data[3]}ft | "
      # Sets heading
      if data[6]:
        formated_string += f"Hdg: {data[6]}° | "
      # Sets aircraft type
      if data[5]:
        formated_string += f"{data[5]}"

      
      # Updates UI to display what is displayed on discord
      status_label.configure(text=formated_string)
      RPC.update(pid=1, details=formated_string, start=data[7])
  
  # Reupdates every 15 seconds
  root.after(15000, update_presence)

# RPC connection
connect_to_discord()
# Main loop for UI
root.mainloop()

