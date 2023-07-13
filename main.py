import yaml
import asyncio
import logging
import sched, time
from kasa import SmartBulb

## Logging Configuration
LOG_LEVEL = logging.INFO
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter("%(message)s")#("%(asctime)s - %(levelname)s: %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

## Definitions

def read_config(filename):
    with open(filename) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS = output.get("Bulbs")
    COLOR_VALUES = output.get("Colors")
    ROUTINES = output.get("Routines")
    logger.debug(f"Configuration Imported:\n\nAvailable Devices:{DEVICE_IPS}\nAvailable Colors:{COLOR_VALUES}\nRoutines:{ROUTINES}\n\n")
    return DEVICE_IPS, COLOR_VALUES, ROUTINES

# Routines
def parse_routine(r):
    type  = r.get("Type")
    bulbs = r.get("Bulbs")
    colors = r.get("Colors")
    brightness = r.get("Brightness")
    interval = r.get("Interval")
    logger.debug(f"Routine Properties:\n\nType: {type}\nDevices: {bulbs}\nColors: {colors}\nInterval: {interval}s\n")
    return type, bulbs, colors, interval

async def execute_routine(routine):
    jobs = set()
    type, bulbs, colors, interval = parse_routine(routine)
    for b in bulbs:
        await smooth_rotate(b, colors, interval)
        
# Lighting Effects
async def smooth_rotate(device, colors, interval):
    b = SmartBulb(DEVICE_IPS[device])
    await b.update()
    for c in colors:
        hue, sat, val = COLOR_VALUES[c]
        logger.debug(f"Changing {device} to {c}; Hue:{hue}, Sat:{sat}, Val:{val}")
        await b.set_hsv(hue, sat, val, transition=interval*1000)
        await asyncio.sleep(interval)
        
# Globals from config
DEVICE_IPS, COLOR_VALUES, ROUTINES = read_config("config.yaml")

async def main():
    #Scheduler = sched.scheduler(time.monotonic, time.sleep)
    routines = set()
    for i in list(range(len(ROUTINES))):
        routine = ROUTINES[i]
        #await execute_routine(routine)
        # Queue up all routines and execute in parallel
        jobs = asyncio.create_task(execute_routine(routine))
        routines.add(jobs)
        jobs.add_done_callback(routines.discard)
    logger.info(f"{jobs}")
    await jobs 


if __name__ == "__main__":
    asyncio.run(main())