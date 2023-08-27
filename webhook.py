from flask import Flask,request,json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def receive_webhook():
    if request.method == "GET":
        pass
    if request.method == "POST":
        data = request.json
        return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)