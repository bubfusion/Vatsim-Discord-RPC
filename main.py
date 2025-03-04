from pypresence import Presence
import tkinter as tk
import customtkinter as ctk
from update import check_for_update
from CTkMessagebox import CTkMessagebox
import webbrowser
import vatsim_api
import logging_setup
import config_setup

# pyinstaller main.py --onefile --icon=VATSIM.ico --add-data "VATSIM.ico;." -w -n Vatsim-Discord-RPC
version = "v1.0.2"
up_to_date = check_for_update(version=version)
log = logging_setup.setup_logging()

config, ini_file_path = config_setup.get_config()

# Discord dev client id
client_id = "1344534564244160662"
RPC = Presence(client_id)

# UI setup
root = ctk.CTk()
root.title("VATSIM Discord Rich Presence")
root.geometry("450x200")
root.wm_iconbitmap(config_setup.resource_path("VATSIM.ico"))
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

def submit():
  '''Runs after clicking submit. Obtains and updates RPC data and .ini if needed'''
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
      if data[0] == 0:
        formated_string, start_time = vatsim_api.format_pilot(data)
      else:
        formated_string, start_time = vatsim_api.fortmat_controller(data)
      
      # Updates UI to display what is displayed on discord
      status_label.configure(text=formated_string)
      RPC.update(pid=1, details=formated_string, start=start_time)
  
  # Reupdates every 15 seconds
  root.after(15000, update_presence)

# RPC connection
connect_to_discord()
# Main loop for UI
root.mainloop()

