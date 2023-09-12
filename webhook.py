import asyncio, yaml
from fastapi import FastAPI
from pydantic import BaseModel
from controller import execute_routine


def read_presents(presentFile, configFile):
    # New keys can be added here
    with open(presentFile) as f:
        output = yaml.safe_load(f)
        presents = output.get("Presents")
    with open(configFile) as f:
        output = yaml.safe_load(f)
        ips = output.get("Devices")
    return presents, ips

PRESENTS, DEVICE_IPS = read_presents("presents.yaml", "config.yaml")

class Present(BaseModel):
    present: str

app = FastAPI()

@app.post("/")
async def receive_webhook(present: Present):
    return present
    #await execute_routine([PRESENTS[present]])
    #return "200"

@app.get("/")
async def root():
    return PRESENTS["Test"]
