import schedule, time, logging
from datetime import datetime, timedelta
from suntime import Sun

from api import execute_routine
from logger import configure_logger
from globals import read_config


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
    elif time.lower() == "sunset":
        final = (SUNSET + timedelta(hours=offset)).strftime("%H:%M")
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


logger = configure_logger(__name__, logging.DEBUG)

# Globals from config
DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config()

sun = Sun(30.271041325306694, -97.74181978453979)

SUNRISE = sun.get_local_sunrise_time()
SUNSET = sun.get_local_sunset_time()


def main():
    for r in ROUTINES:
        if SCHEDULES[r["Schedule"]]["End"] == None:
            schedule_onetime_routines(r)
    logger.info(
        f"Starting service at {datetime.now()}\n\
               Sunrise: {SUNRISE}; Sunset: {SUNSET}\n\
               First run at {schedule.next_run()}"
    )
    while True:
        for r in ROUTINES:
            if SCHEDULES[r["Schedule"]]["End"] != None:
                schedule_continuous_routines(r)  # Need to test this better
        # logger.debug(f"{pformat(schedule.get_jobs())}\n")
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
