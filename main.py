import yaml
import asyncio
import logging
from datetime import datetime, timedelta
import schedule, time
#from suntime import Sun, SunTimeException
from kasa import SmartDevice, SmartBulb, SmartDimmer
from pprint import pprint

## Logging Configuration
LOG_LEVEL = logging.DEBUG
# Main module logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

schedule_logger = logging.getLogger("schedule")
schedule_logger.setLevel(LOG_LEVEL)
schedule_logger.addHandler(sh)

# Config
def read_config(filename):
    # New keys can be added here
    keys = ["Devices", "Colors", "Routines", "Schedules"]
    with open(filename) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS, COLOR_VALUES, ROUTINES, SCHEDULES = [output.get(k) for k in keys]
    return DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES

# Scheduling
def schedule_continuous_routines(routine):
    start = SCHEDULES[routine["Schedule"]]["Start"]
    end   = SCHEDULES[routine["Schedule"]]["End"]
    delta = datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")
    logger.debug(f"{routine} Start: {start}; End: {end}, Delta {delta}")
    if delta < timedelta(): # Find future time if delta returns past one
        delta = delta + timedelta(days=1)
    schedule.every().day.at(start).until(delta).do(execute_routine, routine=routine)

def schedule_onetime_routines(routine):
    start = SCHEDULES[routine["Schedule"]]["Start"]
    #schedule.every().day.at(start).do(execute_routine, routine=routine)
    schedule.every(2).seconds.do(execute_routine, routine=routine)
    logger.debug(f"{routine} Start: {start}")

def execute_routine(routine):
    devices = routine.get("Devices")
    # Group synchronous API calls together
    calls = [call_api(routine, d) for d in devices]
    # Call an event loop and initiate API calls
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*calls))

# API Calls
async def call_api(routine, device):
    call = routine["Devices"][device]
    type, colors, brightness, interval = [call[k] for k in ["Type", "Colors", "Brightness", "Interval"]]
    transition = interval*1000 # ms to seconds for smooth transition
    b = SmartDevice(DEVICE_IPS[device])
    await b.update()

    if b.is_color == False:
        b = SmartDimmer(DEVICE_IPS[device])
    else:
        b = SmartBulb(DEVICE_IPS[device])
    await b.update()

    match type:
        case "power_on":
            await b.set_brightness(1)
            await b.update()
            await b.turn_on()
            await b.set_brightness(brightness, transition=transition)
            logger.debug(f" POST {device}@{DEVICE_IPS[device]} | Turn On | Brightness: {brightness}; Interval: {interval}\n")
        case "power_off":
            await b.turn_off(transition=transition)
            logger.debug(f" POST {device}@{DEVICE_IPS[device]} | Turn Off | Interval: {interval}\n")
        case "smooth_rotate":
            for c in colors:
                hue, sat = COLOR_VALUES[c]
                val = brightness
                await b.set_hsv(hue, sat, val, transition=transition)
                await asyncio.sleep(interval)
            logger.debug(f" POST {device}@{DEVICE_IPS[device]} | Rotate | Color: {c}; Brightness: {brightness}; Interval: {interval}\n")
# Globals from config
DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config("config.yaml")

def main():
    for r in ROUTINES:
        if SCHEDULES[r["Schedule"]]["End"] == None:
            schedule_onetime_routines(r)
    schedule.run_all()



if __name__ == "__main__":
    main()