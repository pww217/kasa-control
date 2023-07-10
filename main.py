import yaml
import asyncio
import sched, time
from kasa import SmartBulb

def read_config(filename):
    with open(filename) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS = output.get("Bulbs")
    COLOR_VALUES = output.get("Colors")
    ROUTINES = output.get("Routines")
    return DEVICE_IPS, COLOR_VALUES, ROUTINES

async def parse_routine(r):
    type  = r.get("Type")
    bulbs = r.get("Bulbs")
    colors = r.get("Colors")
    interval = r.get("Interval")
    return type, bulbs, colors, interval



# Lighting Effects
async def smooth_rotate(bulbs, colors, interval):
    for n in bulbs:
        b = SmartBulb(DEVICE_IPS[n])
        await b.update()
        for c in colors:
            hue, sat, val = COLOR_VALUES[c]
            print(hue, sat, val)
            await b.set_hsv(hue, sat, val)
            print(f"Transitioned {n} to {c}\n")
            await asyncio.sleep(interval)
        

DEVICE_IPS, COLOR_VALUES, ROUTINES = read_config("config.yaml")

async def main():
    #s = sched.scheduler(time.monotonic, time.sleep)
    print(COLOR_VALUES)
    to_schedule = list(range(len(ROUTINES)))
    for r in to_schedule:
        type, bulbs, colors, interval = await parse_routine(ROUTINES[r])
        match type:
            case "smooth_rotate":
                await smooth_rotate(bulbs, colors, interval)
        
        




if __name__ == "__main__":
    asyncio.run(main())