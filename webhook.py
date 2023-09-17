import yaml
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from controller import execute_routine
from logger import configure_logger


def read_presents(presentFile, configFile):
    # New keys can be added here
    with open(presentFile) as f:
        output = yaml.safe_load(f)
        presents = output
    with open(configFile) as f:
        output = yaml.safe_load(f)
        ips = output.get("Devices")
    return presents, ips


async def receive_call(present):
    present = PRESENTS[present]
    execute_routine(present, "webhook")
    return 200


configure_logger(__name__, "debug")
configure_logger("controller", "debug")

PRESENTS, DEVICE_IPS = read_presents("presents.yaml", "config.yaml")


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
