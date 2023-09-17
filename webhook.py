import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from logger import configure_logger
from globals import read_config, read_presents
from api import execute_routine

logger = configure_logger(__name__, logging.DEBUG)


async def receive_call(present):
    present = PRESENTS[present]
    await execute_routine(present, "webhook")
    return 200


DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config()
PRESENTS = read_presents()


class Present(BaseModel):
    present: str


app = FastAPI(
    title="Kasa-Control Webhook Server",
    description="A control server and repository of configuration information",
    summary="See docs",
    version="1.2.0",
)


@app.post("/")
async def root(present: Present):
    return await receive_call(dict(present)["present"])


@app.get("/")
async def redirect():
    return RedirectResponse("/docs/")


@app.get("/p/")
async def parse_query(present: str):
    return await receive_call(present)


@app.get("/colors/")
async def root():
    return COLOR_VALUES


@app.get("/devices/")
async def root():
    return DEVICE_IPS


@app.get("/presents/")
async def root():
    return PRESENTS


@app.get("/routines/")
async def root():
    return ROUTINES


@app.get("/schedules/")
async def root():
    return SCHEDULES
