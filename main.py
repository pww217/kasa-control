import yaml
import asyncio
import logging
import schedule, time
from kasa import SmartBulb
from pprint import pprint


## Logging Configuration
LOG_LEVEL = logging.DEBUG
# Main module logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter("%(levelname)s:%(message)s")#("%(asctime)s - %(levelname)s: %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

schedule_logger = logging.getLogger("schedule")
schedule_logger.setLevel(LOG_LEVEL)
schedule_logger.addHandler(sh)

def read_config(filename):
    # New keys can be added here
    keys = ["Bulbs", "Colors", "Routines", "Schedules"]

    with open(filename) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS, COLOR_VALUES, ROUTINES, SCHEDULES = [output.get(k) for k in keys]
    return DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES

def schedule_routine(routine):
    start = SCHEDULES[routine["Schedule"]]["Start"]
    end   = SCHEDULES[routine["Schedule"]]["End"]
    schedule.every(10).seconds.do(execute_routine, routine=routine)

def execute_routine(routine):
    devices = routine.get("Devices")
    # Group synchronous API calls together
    calls = [call_api(routine, d) for d in devices]
    # Call an event loop and initiate API calls
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*calls))

async def call_api(routine, device):
    calls = routine["Devices"][device]
    type, colors, brightness, interval = [calls[k] for k in ["Type", "Colors", "Brightness", "Interval"]]
    b = SmartBulb(DEVICE_IPS[device])
    transition = interval # Required due to logic of hard vs smooth rotation
    await b.update()
    match type:
        case "smooth_rotate":
            # ms to seconds for smooth transition
            transition = interval*1000
    for c in colors:
        hue, sat = COLOR_VALUES[c]
        val = brightness
        await b.set_hsv(hue, sat, val, transition=transition)
        logger.debug(f" POST {device}@{DEVICE_IPS[device]} | Color: {c}; Brightness: {brightness}; Interval: {interval}\n")
        await asyncio.sleep(interval)

# Globals from config
DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config("config.yaml")

def main():
    for r in ROUTINES:
        schedule_routine(r)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()