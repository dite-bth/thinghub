# -*- coding: utf-8 -*-
from flask import Flask, json, request

app = Flask(__name__)

@app.route("/lightmanager")
def index():
    return "Hello"

@app.route('/lightmanager/<actor>', methods=['POST'])
def set_thingactor(actor):
    data = json.loads(request.get_data())
    return '{"Light1":' + str(data['value']) + '}'


@app.route('/lightmanager/<sensor>', methods=['GET'])
def get_thingsensor(sensor):
    return '{"Luminosity": 0.636}'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
