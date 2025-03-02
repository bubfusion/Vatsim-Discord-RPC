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
def get_pilot_info(user_cid):
    response = requests.get(vatsim_api)
    if response.status_code == 200:
        data = response.json()
        pilots = data.get("pilots", [])
        for pilot in pilots:
            if pilot.get("cid") == user_cid:
                log.info(f"Pilot info: {pilot}")
                return pilot
        log.info("User is offline")
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
  except Exception as e:
    log.error(e)
    return None