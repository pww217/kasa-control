import logging
from datetime import datetime
from asyncio import get_event_loop, gather, sleep
from kasa import SmartDevice, SmartBulb, SmartDimmer

from logger import configure_logger
from globals import read_config

DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config()

logger = configure_logger(__name__, logging.INFO)


def execute_routine(routine, module="controller"):
    devices = routine["Devices"]
    # Group synchronous API calls together
    calls = [call_api(routine, d) for d in devices]
    # Call an event loop and initiate API calls
    if module == "webhook":
        gather(*calls)
    elif module == "controller":
        logger.info(
            f"Executing Routine {routine['Schedule']} on {datetime.now().strftime('%A at %H:%M%S')}"
        )
        loop = get_event_loop()  # Main usage
        loop.run_until_complete(gather(*calls))


# API Calls
async def call_api(routine, device):
    call = routine["Devices"][device]
    type, colors, brightness, interval = (
        call[k] for k in ["Type", "Colors", "Brightness", "Interval"]
    )
    transition = interval * 1000  # ms to seconds for smooth transition
    b = SmartDevice(DEVICE_IPS[device])
    await b.update()

    if b.model == "HS220(US)":
        b = SmartDimmer(DEVICE_IPS[device])
    elif b.model == "KL125(US)":
        b = SmartBulb(DEVICE_IPS[device])
    await b.update()

    match type:
        case "set_brightness":
            if b.is_off:
                await b.set_brightness(1)
                await b.turn_on()
            await b.set_brightness(brightness, transition=transition)
            logger.info(
                f"POST {device}@{DEVICE_IPS[device]} | Set Brightness | Brightness: {brightness}; Interval: {interval}"
            )
        case "power_off":
            await b.turn_off(transition=transition)
            logger.info(
                f"POST {device}@{DEVICE_IPS[device]} | Turn Off | Interval: {interval}"
            )
        case "toggle_power":
            if b.is_on:
                await b.turn_off(transition=transition)
                logger.info(
                    f"POST {device}@{DEVICE_IPS[device]} | Turn Off | Interval: {interval}"
                )
            else:
                await b.set_brightness(1)
                await b.turn_on()
                await b.set_brightness(brightness, transition=transition)
                logger.info(
                    f"POST {device}@{DEVICE_IPS[device]} | Turn On | Interval: {interval}"
                )
        case "smooth_rotate":
            for c in colors:
                hue, sat = COLOR_VALUES[c]
                val = brightness
                await b.set_hsv(hue, sat, val, transition=transition)
                await sleep(interval)
            logger.info(
                f"POST {device}@{DEVICE_IPS[device]} | Rotate | Color: {c}; Brightness: {brightness}; Interval: {interval}"
            )
        case _:
            logger.info(
                f"POST {device}@{DEVICE_IPS[device]} | THIS DEVICE DID NOT MATCH A VALID TYPE."
            )
            pass
