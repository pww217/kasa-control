import asyncio, yaml
from fastapi import FastAPI
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


async def main():
    PRESENTS, DEVICE_IPS = read_presents("presents.yaml", "config.yaml")



if __name__ == "__main__":
    main()
