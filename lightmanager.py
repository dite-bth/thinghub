# -*- coding: utf-8 -*-
from flask import Flask, render_template
from bson.json_util import dumps

app = Flask(__name__)

@app.route("/lightmanager")
def index():
    return "Hello"

@app.route('/lightmanager/<actor>/<value>', methods=['POST'])
def set_thingactor(actor, value):
    return '{"Light1":' + str(value) + '}'


@app.route('/lightmanager/<sensor>', methods=['GET'])
def get_thingsensor(sensor):
    return '{"Luminosity": 0.636}'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
