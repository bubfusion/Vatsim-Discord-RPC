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

# pyinstaller main.py --onefile --icon=VATSIM.ico --add-data "VATSIM.ico;." -w -n Vatsim-Discord-RPC
version = "v1.0.1"
up_to_date = check_for_update(version=version)

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

# API for Vatsim data
vatsim_api = "https://data.vatsim.net/v3/vatsim-data.json"

'''Returns pilot data for given CID'''
def get_pilot_info(user_cid):
    response = requests.get(vatsim_api)
    if response.status_code == 200:
        data = response.json()
        pilots = data.get("pilots", [])
        for pilot in pilots:
            if pilot.get("cid") == user_cid:
                return pilot
        return None


'''Returns parsed flight data for given CID'''
def get_data(user_cid):
  try:
    pilot = get_pilot_info(user_cid)
    call_sign = pilot.get("callsign")
    altitude = pilot.get("altitude")
    hdg = pilot.get("heading")

    flight_plan = pilot.get("flight_plan", {})

    # Gets data from flight plan if it exists
    if flight_plan != None:
      departure = flight_plan.get("departure")
      arrival = flight_plan.get("arrival")
      flight_rule_letter = flight_plan.get("flight_rules")

      if(flight_rule_letter == 'I'):
        flight_rule = "IFR"
      elif(flight_rule_letter == 'V'):
        flight_rule= "VFR"
      else:
        flight_rule = None

      aircraft_type = flight_plan.get("aircraft_short")
    # If no flight plan is filed, sets everything to None
    else:
      departure = arrival = flight_rule = aircraft_type = None
      
    # How long user has been logged into network for
    logon_time = (pilot.get("logon_time"))

    # Thank you ChatGPT for this line. Line saver
    dt = datetime.fromisoformat(logon_time.rstrip('Z')).replace(tzinfo=timezone.utc)

    # Get epoch time
    epoch_time = int(dt.timestamp())

    # If sucessfully found user on network, return parsed data
    if(pilot != None):
      return(call_sign, departure, arrival, altitude, flight_rule, aircraft_type, hdg, epoch_time)
    # If no user was found return None
    else:
      return None
  except:
    return None
  
      

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
  # Runs if RPC wrapper can't make connection with discord
  except:
    status_label.configure(text="Please open discord")
    # Checks connection again after 5 seconds
    root.after(5000, connect_to_discord)


'''Updates UI and discord RPC to display flight details'''
def update_presence():
  # Gets data for current cid
  data = get_data(cid)

  # Makes sure pilot is online and exists
  if(data!= None):
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
  # If there is no pilot data, means CID is wrong or user is offline
  else:
    status_label.configure(text="User is offline or invalid")

    # Clears RPC
    RPC.clear(1)
  
  # Reupdates every 15 seconds
  root.after(15000, update_presence)

# RPC connection
connect_to_discord()
# Main loop for UI
root.mainloop()

