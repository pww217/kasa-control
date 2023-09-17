import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from logger import configure_logger
from globals import get_device_ips, read_presents

from api import execute_routine

logger = configure_logger(__name__, logging.DEBUG)


async def receive_call(present):
    present = PRESENTS[present]
    await execute_routine(present, "webhook")
    return 200


DEVICE_IPS = get_device_ips()
PRESENTS = read_presents()


class Present(BaseModel):
    present: str


app = FastAPI()


@app.post("/")
async def root(present: Present = str):
    return await receive_call(dict(present)["present"])


@app.get("/")
async def root():
    return PRESENTS


@app.get("/p/")
async def parse_query(present: str):
    # try:
    return await receive_call(present)
    # except:
    #    return 'failure'
