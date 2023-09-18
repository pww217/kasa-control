import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from globals import read_config, read_presents
from api import execute_routine


async def receive_call(present):
    present = PRESENTS[present]
    try:
        return execute_routine(present, "webhook")
    except KeyError:
        return "That present does not exist. Check /presents/ for options."


DEVICE_IPS, COLOR_VALUES, SCHEDULES, ROUTINES = read_config()
PRESENTS = read_presents()


class Present(BaseModel):
    present: str


app = FastAPI(
    title="Kasa-Control Webhook Server",
    description="A control server and repository of configuration information",
    version="1.2.1",
)


@app.get("/")
async def redirect():
    return RedirectResponse("/docs/")


@app.post("/")
async def root(present: Present):
    return await receive_call(dict(present)["present"])


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
