import requests
from datetime import datetime, timezone
import logging_setup

log = logging_setup.setup_logging()

# API for Vatsim data
vatsim_api = "https://data.vatsim.net/v3/vatsim-data.json"
vatsim_user_api = "https://api.vatsim.net/v2/members/"

def valid_cid(user_cid):
  response = requests.get(vatsim_user_api + str(user_cid))
  if response.status_code == 200:
    log.info("Valid CID")
    return True
  else:
    log.warning(f"Invalid CID: {user_cid}")
    return False
    

'''Returns pilot data for given CID'''
def get_user_info(user_cid):
    response = requests.get(vatsim_api)
    if response.status_code == 200:
        data = response.json()
        pilots = data.get("pilots", [])
        controllers = data.get("controllers", [])
        for pilot in pilots:
            if pilot.get("cid") == user_cid:
                log.info(f"Pilot info: {pilot}")
                return (pilot, 0)
        for controller in controllers:
          if controller.get("cid") == user_cid:
            print(f"Controller info: {controller}")
            log.info(f"Controller info: {controller}")
            return (controller,1)
        log.info("User is offline")
        return None


'''Returns parsed flight data for given CID'''
def get_data(user_cid):
  data = get_user_info(user_cid)
  print(data)
  try:
    if data[1] == 0:
      
        pilot = data[0]
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
          return(0,call_sign, departure, arrival, altitude, flight_rule, aircraft_type, hdg, epoch_time)
        # If no user was found return None
        else:
          return None
    elif data[1] == 1:
        controller = data[0]
        call_sign = controller.get("callsign")
        freq = controller.get("frequency")

        # How long user has been logged into network for
        logon_time = (controller.get("logon_time"))

        # Thank you ChatGPT for this line. Line saver
        dt = datetime.fromisoformat(logon_time.rstrip('Z')).replace(tzinfo=timezone.utc)

        # Get epoch time
        epoch_time = int(dt.timestamp())

        rating = controller.get("rating")

        rating_string = ""

        match rating:
          case -1:
            rating_string = "INA"
          case 0:
            rating_string = "SUS"
          case 1:
            rating_string = "OBS"
          case 2:
            rating_string = "S1"
          case 3:
            rating_string = "S2"
          case 4:
            rating_string = "S4"
          case 5:
            rating_string = "C1"
          case 6:
            rating_string = "C2"
          case 7:
            rating_string = "C3"
          case 8:
            rating_string = "I1"
          case 9:
            rating_string = "I2"
          case 10:
            rating_string = "I3"
          case 11:
            rating_string = "SUP"
          case 12:
            rating_string = "ADM"

        # If sucessfully found user on network, return parsed data
        if(controller != None):
          return(1, call_sign, freq, rating_string, epoch_time)
        # If no user was found return None
        else:
          return None
    else:
      return None
  except Exception as e:
    log.error(e)
  
def format_pilot(data):
  formated_string = ""
  # Sets depature airport
  if data[2]:
    formated_string += f"{data[2]}"
  # Sets arrival airport
  if data[3]:
    formated_string += f"➜{data[3]} | "
  # If no arrival airport, but has depature
  elif data[2]:
    formated_string += f" | "
  # Sets callsign
  if data[1]:
    formated_string += f"Callsign: {data[1]} | "
  # Sets flight rules
  if data[5]:
    formated_string += f"{data[5]} | "
  # Sets altitude
  if data[4]:
    formated_string += f"Alt: {data[4]}ft | "
  # Sets heading
  if data[7]:
    formated_string += f"Hdg: {data[7]}° | "
  # Sets aircraft type
  if data[6]:
    formated_string += f"{data[6]}"

  return (formated_string, data[8])

def fortmat_controller(data):
  # return(1, call_sign, freq, rating_string, epoch_time)
  formated_string = ""
  if data[1]:
    formated_string += f"{data[1]} | "
  if data[2]:
    formated_string += f"Frequency: {data[2]} | "
  if data[3]:
    formated_string += f"Rating: {data[3]}"
  
  return (formated_string, data[4])

