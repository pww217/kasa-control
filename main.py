import yaml
import asyncio
import logging
import schedule, time
from kasa import SmartBulb


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

def parse_routine(r):
    # New keys can be added here
    keys = ["Name", "Type", "Bulbs", "Colors", "Brightness", "Interval", "Schedule"]

    name, type, bulbs, colors, brightness, interval, schedule = [r.get(k) for k in keys]
    return name, type, bulbs, colors, brightness, interval, schedule

async def call_api(bulb, type, colors, brightness, interval):
    b = SmartBulb(DEVICE_IPS[bulb])
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
        logger.debug(f" POST {bulb}@{DEVICE_IPS[bulb]} | Color: {c}; Brightness: {brightness}; Interval: {interval}\n")
        await asyncio.sleep(interval)

def execute_routine(routine):
    name, type, bulbs, colors, brightness, interval, schedule = parse_routine(routine)
    # Gather all API calls for a routine and execute in parallel
    calls = [call_api(b, type, colors, brightness, interval) for b in bulbs]
    logger.info(f"Running {name}\n")
    logger.debug(f"Type: {type}\nDevices: {bulbs}\nColors:{colors}\nBrightness:{brightness}\nInterval:{interval}\nSchedule:{schedule}\n")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*calls))
    logger.info(f"{name} complete.\n")

# Globals from config
DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config("config.yaml")

def schedule_routine(routine):
    start = SCHEDULES[routine["Schedule"]]["Start"]
    end   = SCHEDULES[routine["Schedule"]]["End"]
    #schedule.every(2).seconds.do(print, "hello")
    schedule.every(1).seconds.do(execute_routine, routine=routine)
    #s = schedule.every().day.at(routine["Start"]).do(asyncio.run(execute_routine, routine=routine))

def main():
    # List comprehension groups all routines for parallel execution
    #routines = [execute_routine(i) for i in list(range(len(ROUTINES)))]
    for r in ROUTINES:
        schedule_routine(r)
    while True:
        #job = asyncio.gather(*routines)
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()