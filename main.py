import yaml
import asyncio
import logging
import sched, time
from suntime import Sun, SunTimeException
from kasa import SmartBulb

## Logging Configuration
LOG_LEVEL = logging.INFO
# Main module logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter("%(message)s")#("%(asctime)s - %(levelname)s: %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

def read_config(filename):
    keys = ["Bulbs", "Colors", "Routines", "Schedules"]

    with open(filename) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS, COLOR_VALUES, ROUTINES, SCHEDULES = [output.get(k) for k in keys]
    return DEVICE_IPS, COLOR_VALUES, ROUTINES, SCHEDULES

def parse_routine(r):
    keys = ["Type", "Bulbs", "Colors", "Brightness", "Interval", "Schedule"]

    type, bulbs, colors, brightness, interval, schedule = [r.get(k) for k in keys]
    logger.debug(f"Routine Properties:\n\nType: {type}\nDevices: {bulbs}\nColors:\
                 {colors}\nInterval: {interval}s; Schedule: {schedule}\n")
    return type, bulbs, colors, brightness, interval, schedule

async def access_device(device):
    b = SmartBulb(DEVICE_IPS[device])
    await b.update()
    return b

async def call_api(b, type, colors, brightness, interval):
    logger.info(f"\nBeginning Routine\n\nType: {type}; Bulb: {b}; Colors:{colors};\nBrightness:{brightness}; Interval:{interval}")
    if brightness is not None:
        await set_brightness(b, brightness, interval)
    await rotate_lights(b, type, colors, interval)

async def execute_routine(routine):
    type, bulbs, colors, brightness, interval, schedule = parse_routine(ROUTINES[routine])
    # Similar to main(), gather all API calls for a routine and execute in parallel
    calls = [call_api(b, type, colors, brightness, interval) for b in bulbs]
    await asyncio.gather(*calls)
        

# Lighting Effects
async def rotate_lights(device, type, colors, interval):
    match type:
        case "smooth_rotate":
            interval = interval*1000
    b = await access_device(device)
    for c in colors:
        hue, sat, val = COLOR_VALUES[c]
        logger.debug(f"Changing {device} to {c}; Hue:{hue}, Sat:{sat}, Val:{val}")
        await b.set_hsv(hue, sat, val, transition=interval)
        await asyncio.sleep(interval)

async def set_brightness(device, brightness, interval):
    b = await access_device(device)
    logger.debug(f"Changing brightness of {device} to {brightness}")
    await b.set_brightness(brightness, transition=interval*1000)
    await asyncio.sleep(interval)

        
# Globals from config
DEVICE_IPS, COLOR_VALUES, ROUTINES, SCHEDULES = read_config("config.yaml")

async def main():
    #s = sched.scheduler(time.monotonic, time.sleep)
    # List comprehension groups all routines for parallel execution
    routines = [execute_routine(i) for i in list(range(len(ROUTINES)))]
    await asyncio.gather(*routines)

if __name__ == "__main__":
    asyncio.run(main())