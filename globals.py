import yaml

config_file = "config.yaml"

present_file = "presents.yaml"


def get_device_ips(config_file=config_file):
    with open(config_file) as f:
        output = yaml.safe_load(f)
    DEVICE_IPS = output.get("Devices")
    return DEVICE_IPS


def read_config(config_file=config_file):
    # New keys can be added here
    keys = ["Colors", "Routines", "Schedules"]
    with open(config_file) as f:
        output = yaml.safe_load(f)
    COLOR_VALUES, ROUTINES, SCHEDULES = [output.get(k) for k in keys]
    return COLOR_VALUES, SCHEDULES, ROUTINES


def read_presents(present_file=present_file):
    # New keys can be added here
    with open(present_file) as f:
        output = yaml.safe_load(f)
        presents = output
    return presents