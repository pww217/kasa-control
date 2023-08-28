from flask import Flask, request, json

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def receive_webhook():
    if request.method == "POST":
        data = request.json
        return data


"""
[{
  'type': 'set_brightness',
  'devices': [
    LivingRoom,
    LivingRoomAux
  ],
  'brightness': 50
  'transition': 15
},
{
  'type': 'power_off',
  'devices': [
    Kitchen
  ],
  'brightness': 50
  'transition': 15
}]
"""


app.run(host="0.0.0.0", debug=True)
