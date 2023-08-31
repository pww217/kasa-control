import yaml
from flask import Flask, request, json
from controller import call_api

def read_presents(presentFile, configFile):
    # New keys can be added here
    with open(presentFile) as f:
        output = yaml.safe_load(f)
        presents = output.get('Presents')
    with open(configFile) as f:
        output = yaml.safe_load(f)
        ips = output.get('Devices')
    return presents, ips

def main():
  PRESENTS, DEVICE_IPS = read_presents('presents.yaml', 'config.yaml')

  app = Flask(__name__)

  @app.route("/", methods=["GET", "POST"])
  def receive_webhook():
    if request.method == "POST":
        data = request.json
        return data["Present"]

  app.run(host="0.0.0.0", debug=True)

if __name__ == "__main__":
    main()