import yaml, asyncio, logging, schedule, time
from pprint import pformat
from datetime import datetime, timedelta
from suntime import Sun, SunTimeException
from kasa import SmartDevice, SmartBulb, SmartDimmer

## Logging Configuration
# Main
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s-%(levelname)s: %(message)s", "%H:%M:%S")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
# Schedule
schedule_logger = logging.getLogger("schedule")
schedule_logger.setLevel(logging.DEBUG)
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
    end = SCHEDULES[routine["Schedule"]]["End"]
    delta = datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")
    logger.debug(f"{routine} Start: {start}; End: {end}, Delta {delta}")
    if delta < timedelta():  # Find future time if delta returns past one
        delta = delta + timedelta(days=1)
    schedule.every().day.at(start).until(delta).do(execute_routine, routine=routine)


def schedule_sun_routine(start, char, routine):
    if char == None:  # For when no offset
        time = start
        offset = 0
    else:
        time, offset = start.split(char)  # For offset
        offset = float(offset)
    if char == "-":  # Negate offset if requested
        offset = -offset
    if time.lower() == "sunrise":
        final = (SUNRISE + timedelta(hours=offset)).strftime("%H:%M")
        logger.debug(f"Time: {time}; Operation: {char}; Offset: {offset}h")
    elif time.lower() == "sunset":
        final = (SUNSET + timedelta(hours=offset)).strftime("%H:%M")
        logger.debug(f"Time: {time}; Operation: {char}; Offset: {offset}h")
    schedule.every().day.at(final).do(execute_routine, routine=routine)
    logger.debug(f"{routine} Start: {final}; Offset: {offset}")


def schedule_onetime_routines(routine):
    start = SCHEDULES[routine["Schedule"]]["Start"]
    if "sun" in start.lower():
        if "-" in start:
            schedule_sun_routine(start, "-", routine)
        elif "+" in start:
            schedule_sun_routine(start, "+", routine)
        else:
            schedule_sun_routine(start, None, routine)
    else:
        schedule.every().day.at(start).do(execute_routine, routine=routine)
        logger.debug(f"{routine} Start: {start}")


def execute_routine(routine):
    devices = routine["Devices"]
    # Group synchronous API calls together
    calls = [call_api(routine, d) for d in devices]
    # Call an event loop and initiate API calls
    loop = asyncio.get_event_loop()
    logger.info(f"Executing {routine['Schedule']}")
    loop.run_until_complete(asyncio.gather(*calls))


# API Calls
async def call_api(routine, device):
    call = routine["Devices"][device]
    type, colors, brightness, interval = [
        call[k] for k in ["Type", "Colors", "Brightness", "Interval"]
    ]
    transition = interval * 1000  # ms to seconds for smooth transition
    b = SmartDevice(DEVICE_IPS[device])
    await b.update()

    if b.model == "HS220(US)":
        b = SmartDimmer(DEVICE_IPS[device])
    elif b.model == "KL125(US)":
        b = SmartBulb(DEVICE_IPS[device])
    await b.update()

    match type:
        case "on":
            await b.set_brightness(1)
            # await b.update()
            await b.turn_on()
            await b.set_brightness(brightness, transition=transition)
            logger.debug(
                f" POST {device}@{DEVICE_IPS[device]} | Turn On | Brightness: {brightness}; Interval: {interval}\n"
            )
        case "off":
            await b.turn_off(transition=transition)
            logger.debug(
                f" POST {device}@{DEVICE_IPS[device]} | Turn Off | Interval: {interval}\n"
            )
        case "set_brightness":
            if b.is_off:
                await b.set_brightness(1)
                # await b.update()
                await b.turn_on()
            await b.set_brightness(brightness, transition=transition)
            logger.debug(
                f" POST {device}@{DEVICE_IPS[device]} | Set Brightness | Brightness: {brightness}; Interval: {interval}\n"
            )
        case "smooth_rotate":
            for c in colors:
                hue, sat = COLOR_VALUES[c]
                val = brightness
                await b.set_hsv(hue, sat, val, transition=transition)
                await asyncio.sleep(interval)
            logger.debug(
                f" POST {device}@{DEVICE_IPS[device]} | Rotate | Color: {c}; Brightness: {brightness}; Interval: {interval}\n"
            )
        case _:
            logger.debug(
                f" POST {device}@{DEVICE_IPS[device]} | THIS DEVICE DID NOT MATCH A VALID TYPE. \n"
            )
            pass


# Globals from config
DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config("config.yaml")
sun = Sun(30.271041325306694, -97.74181978453979)

SUNRISE = sun.get_local_sunrise_time()
SUNSET = sun.get_local_sunset_time()

logger.debug(f"Sunrise: {SUNRISE}; SUNSET: {SUNSET}")


def main():
    for r in ROUTINES:
        if SCHEDULES[r["Schedule"]]["End"] == None:
            schedule_onetime_routines(r)
    counter = 0
    logger.info("Starting service...")
    while True:
        for r in ROUTINES:
            if SCHEDULES[r["Schedule"]]["End"] != None:
                schedule_continuous_routines(r)

        time_until = round(schedule.idle_seconds())
        interval = 60 * 5
        if counter == interval:
            logger.info(
                f"Next run in {timedelta(seconds=time_until)} at {schedule.next_run()}"
            )
            logger.debug(f"\n{pformat(schedule.get_jobs())}\n")
            counter = 0

        schedule.run_pending()
        time.sleep(1)
        counter += 1


if __name__ == "__main__":
    main()
