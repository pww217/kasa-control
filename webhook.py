import yaml, logging
from fastapi import FastAPI
from pydantic import BaseModel
from controller import execute_routine

## Logging Configuration
# Main
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s-%(levelname)s: %(message)s", "%H:%M:%S")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

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
    present = PRESENTS[dict(present)["present"]]
    #return present
    execute_routine(present, "webhook")
    return 200

@app.get("/")
async def root():
    return PRESENTS["Test"]
