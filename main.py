from pypresence import Presence
import requests
import tkinter as tk
import customtkinter as ctk
import os
import configparser


roaming_path = os.path.join(os.getenv('APPDATA'), "VATSIM-Discord-RPC")
if not os.path.exists(roaming_path):
    os.makedirs(roaming_path)

ini_file_path = os.path.join(roaming_path, 'config.ini')

if not os.path.exists(ini_file_path):
    with open(ini_file_path, 'w') as ini_file:
        ini_file.write('[Settings]\n')
        ini_file.write('uid=\n')

config = configparser.ConfigParser()
config.read(ini_file_path)
print(config.get("Settings", "uid"))

vatsim_api = "https://data.vatsim.net/v3/vatsim-data.json"

def get_pilot_info(user_cid):
    response = requests.get(vatsim_api)
    print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        pilots = data.get("pilots", [])
        for pilot in pilots:
            if pilot.get("cid") == user_cid:
                return pilot
        return None

def get_data(user_cid):
  try:
    pilot = get_pilot_info(user_cid)
    call_sign = pilot.get("callsign")
    flight_plan = pilot.get("flight_plan", {})
    departure = flight_plan.get("departure")
    arrival = flight_plan.get("arrival")
    altitude = pilot.get("altitude")
    hdg = pilot.get("heading")

    flight_rule_letter = flight_plan.get("flight_rules")
    if(flight_rule_letter == 'I'):
      flight_rule = "IFR"
    elif(flight_rule_letter == 'V'):
      flight_rule= "VFR"
    else:
      flight_rule = None
      
    aircraft_type = flight_plan.get("aircraft_short")

    if(pilot != None):
      return(call_sign, departure, arrival, altitude, flight_rule, aircraft_type, hdg)
    else:
      return None
  except:
    return None
  
      

client_id = "1344534564244160662"
RPC = Presence(client_id)


root = ctk.CTk()
root.title("VATSIM Discord Rich Presence")
root.geometry("450x200")

uid_var = tk.StringVar()
uid = 0

def submit():
  global uid 
  try:
    uid = int(uid_var.get())
    update_presence()
  except:
    status_label.configure(text="Invalid CID!")

  

uid_label = ctk.CTkLabel(root, text = 'UID', font=('arial ',10, 'bold'))

uid_entry = ctk.CTkEntry(root,textvariable = uid_var, font=('arial ',10,'normal'))
sub_btn= ctk.CTkButton(root,text = 'Submit', command = submit)

uid_label.pack(anchor="center")
uid_entry.pack(anchor="center")

sub_btn.pack(anchor="center")

status_label = ctk.CTkLabel(root, text="Please open discord")
status_label.pack(anchor='center')



def connect_to_discord():
  try:
    status_label.configure(text="RPC connected. Waiting for CID...")
    RPC.connect()
  except:
    status_label.configure(text="Please open discord")
    root.after(5000, connect_to_discord)


def update_presence():
  data = get_data(uid)
  if(data!= None):
    formated_string = ""
    if data[1]:
      formated_string += f"{data[1]}"
    if data[2]:
      formated_string += f"➜{data[2]} | "
    # If no arrival airport, but has depature
    elif data[1]:
      formated_string += f" | "
    if data[0]:
      formated_string += f"Callsign: {data[0]} | "
    if data[4]:
      formated_string += f"{data[4]} | "
    if data[3]:
      formated_string += f"Alt: {data[3]}ft | "
    if data[6]:
      formated_string += f"Hdg: {data[6]}° | "
    if data[5]:
      formated_string += f"{data[5]}"
      
    status_label.configure(text=formated_string)
    RPC.update(pid=1, details=formated_string)
  else:
    status_label.configure(text="ID is offline")
    RPC.clear(1)
    
  root.after(15000, update_presence)

connect_to_discord()
root.mainloop()

