import asyncio, yaml
from flask import Flask, request, json
from controller import call_api, execute_routine


def read_presents(presentFile, configFile):
    # New keys can be added here
    with open(presentFile) as f:
        output = yaml.safe_load(f)
        presents = output.get("Presents")
    with open(configFile) as f:
        output = yaml.safe_load(f)
        ips = output.get("Devices")
    return presents, ips


def main():
    PRESENTS, DEVICE_IPS = read_presents("presents.yaml", "config.yaml")
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def receive_webhook():
        if request.method == "GET":
            return '<h2 align="center">kasa-control webhook server</h2>'
        elif request.method == "POST":
            p = request.json["Present"]
            asyncio.run(execute_routine(PRESENTS[p]))

    app.run(host="0.0.0.0", debug=True)

if __name__ == "__main__":
    main()
