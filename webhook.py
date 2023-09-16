import yaml
from fastapi import FastAPI
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

configure_logger(__name__, 'debug')
configure_logger('controller', 'debug')

PRESENTS, DEVICE_IPS = read_presents("presents.yaml", "config.yaml")

class Present(BaseModel):
    present: str

app = FastAPI()

@app.post("/")
async def receive_webhook(present: Present):
    present = PRESENTS[dict(present)]
    #return present
    execute_routine(present, "webhook")
    return 200

@app.get("/")
async def root():
    return PRESENTS

#@app.get("/p/")
#async def parse_query():
