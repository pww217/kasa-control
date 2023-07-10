import yaml
import asyncio
import logging
import sched, time
from kasa import SmartBulb

## Logging Configuration
LOG_LEVEL = logging.INFO
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

def read_config(filename):
    with open(filename) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS = output.get("Bulbs")
    COLOR_VALUES = output.get("Colors")
    ROUTINES = output.get("Routines")
    logger.debug(f"Configuration Ingested:\n\nAvailable Devices:{DEVICE_IPS}\nAvailable Colors:{COLOR_VALUES}\nRoutines:{ROUTINES}\n")
    return DEVICE_IPS, COLOR_VALUES, ROUTINES

# Routines
async def parse_routine(r):
    type  = r.get("Type")
    bulbs = r.get("Bulbs")
    colors = r.get("Colors")
    interval = r.get("Interval")
    logger.info(f"Routine Properties:\n\nType: {type}\nDevices: {bulbs}\nColors: {colors}\nInterval: {interval}s\n")
    return type, bulbs, colors, interval

async def execute_routine(routine):
    logger.info(f"Beginning routine {routine}")
    type, bulbs, colors, interval = await parse_routine(ROUTINES[routine])
    match type:
        case "smooth_rotate":
            await smooth_rotate(bulbs, colors, interval)
        case _:
            logging.WARNING("Routine did not match any allowed Type")
        
# Lighting Effects
async def smooth_rotate(bulbs, colors, interval):
    for n in bulbs:
        b = SmartBulb(DEVICE_IPS[n])
        await b.update()
        for c in colors:
            hue, sat, val = COLOR_VALUES[c]
            logger.debug(f"Changing {n} to {c}; Hue:{hue}, Sat:{sat}, Val:{val}")
            await b.set_hsv(hue, sat, val, transition=interval*1000)
            await asyncio.sleep(interval)
        

DEVICE_IPS, COLOR_VALUES, ROUTINES = read_config("config.yaml")

async def main():
    Scheduler = sched.scheduler(time.monotonic, time.sleep)
    to_schedule = list(range(len(ROUTINES)))
    for r in to_schedule:
        Scheduler.enter(10000, 3, await execute_routine(r))
        


if __name__ == "__main__":
    asyncio.run(main())