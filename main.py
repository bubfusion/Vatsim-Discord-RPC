from pypresence import Presence
import time
import requests

vatsim_api = "https://data.vatsim.net/v3/vatsim-data.json"

def get_pilot_info(user_cid):
    response = requests.get(vatsim_api)
    
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
    altitude = flight_plan.get("altitude")

    flight_rule_letter = flight_plan.get("flight_rules")
    if(flight_rule_letter == 'I'):
      flight_rule = "IFR"
    elif(flight_rule_letter == 'V'):
      flight_rule= "VFR"
    else:
      flight_rule = None
      
    aircraft_type = flight_plan.get("aircraft_short")

    if(pilot != None):
      return(call_sign, departure, arrival, altitude, flight_rule, aircraft_type)
    else:
      return None
  except:
    return None
      

client_id = "1344534564244160662"
RPC = Presence(client_id)

RPC.connect()
id = 1644977
while True:
  data = get_data(id)
  if(data!= None):
    RPC.update(pid=1, details=f"{data[1]}➜{data[2]} | Callsign: {data[1]} | {data[4]} | Alt: {data[3]}ft")
    time.sleep(15)
  else:
    RPC.clear(1)
    time.sleep(60)