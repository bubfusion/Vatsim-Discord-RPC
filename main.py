from pypresence import Presence
import time
import requests
import tkinter as tk


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

RPC.connect()

root = tk.Tk()
root.title("VATSIM Discord Rich Presence")
root.geometry("400x200")

uid_var = tk.IntVar()
uid = 0

def submit():
  global uid 
  uid = uid_var.get()
  update_presence()

uid_label = tk.Label(root, text = 'UID', font=('calibre',10, 'bold'))
uid_entry = tk.Entry(root,textvariable = uid_var, font=('calibre',10,'normal'))
sub_btn=tk.Button(root,text = 'Submit', command = submit)

uid_label.grid(row=0,column=0)
uid_entry.grid(row=0,column=1)

sub_btn.grid(row=1,column=1)

status_label = tk.Label(root, text="Waiting for CID...")
status_label.grid(row=2, column=0)

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
      formated_string += f"{data[5]} | "
      
    status_label.config(text=formated_string)
    RPC.update(pid=1, details=formated_string)
  else:
    status_label.config(text="ID is offline")
    RPC.clear(1)
    
  root.after(15000, update_presence)

root.mainloop()

