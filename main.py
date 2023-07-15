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
    with open(filename) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS = output.get("Bulbs")
    COLOR_VALUES = output.get("Colors")
    ROUTINES = output.get("Routines")
    SCHEDULES = output.get("Schedules")
    return DEVICE_IPS, COLOR_VALUES, ROUTINES, SCHEDULES

# Routines
def parse_routine(r):
    # Attempt to compress this.
    #keys = ["Type", "Bulbs", "Colors", "Brightness", "Interval", "Schedule"]
    #for k keys:
    #    k = r.get(k)
    type  = r.get("Type")
    bulbs = r.get("Bulbs")
    colors = r.get("Colors")
    brightness = r.get("Brightness")
    interval = r.get("Interval")
    schedule = r.get("Schedule")
    logger.debug(f"Routine Properties:\n\nType: {type}\nDevices: {bulbs}\nColors:\
                 {colors}\nInterval: {interval}s; Schedule: {schedule}\n")
    return type, bulbs, colors, brightness, interval, schedule

async def call_api(b, type, colors, brightness, interval):
    logger.info(f"\nBeginning Routine\n\nType: {type}; Bulb: {b}; Colors:{colors};\nBrightness:{brightness}; Interval:{interval}")
    if brightness is not None:
        await set_brightness(b, brightness, interval)
    match type:
        case "smooth_rotate":
            await smooth_rotate(b, colors, interval)
        case "hard_rotate":
            await hard_rotate(b, colors, interval)

async def execute_routine(routine):
    type, bulbs, colors, brightness, interval, schedule = parse_routine(ROUTINES[routine])
    calls = [call_api(b, type, colors, brightness, interval) for b in bulbs]
    logger.info(calls)
    await asyncio.gather(*calls)
        

# Lighting Effects
async def smooth_rotate(device, colors, interval):
    b = SmartBulb(DEVICE_IPS[device])
    await b.update()
    for c in colors:
        hue, sat, val = COLOR_VALUES[c]
        #logger.debug(f"Changing {device} to {c}; Hue:{hue}, Sat:{sat}, Val:{val}")
        await b.set_hsv(hue, sat, val, transition=interval*1000)
        await asyncio.sleep(interval)

async def hard_rotate(device, colors, interval):
    b = SmartBulb(DEVICE_IPS[device])
    await b.update()
    for c in colors:
        hue, sat, val = COLOR_VALUES[c]
        #logger.debug(f"Changing {device} to {c}; Hue:{hue}, Sat:{sat}, Val:{val}")
        await b.set_hsv(hue, sat, val, transition=interval*1000)

async def set_brightness(device, brightness, interval):
    b = SmartBulb(DEVICE_IPS[device])
    await b.update()
    #logger.debug(f"Changing brightness of {device} to {brightness}")
    await b.set_brightness(brightness, transition=interval*1000)

        
# Globals from config
DEVICE_IPS, COLOR_VALUES, ROUTINES, SCHEDULES = read_config("config.yaml")

async def main():
    #s = sched.scheduler(time.monotonic, time.sleep)
    routines = [execute_routine(i) for i in list(range(len(ROUTINES)))]
    await asyncio.gather(*routines)

if __name__ == "__main__":
    asyncio.run(main())