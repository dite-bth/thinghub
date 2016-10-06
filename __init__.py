# -*- coding: utf-8 -*-
import json, urllib, urllib2, requests, gevent
from flask import Flask, render_template, Response, request
from bson.json_util import dumps
from pymongo import MongoClient
from gevent.wsgi import WSGIServer
from gevent.queue import Queue
from sse import ServerSentEvent
from subscriptions import Subscriptions

app = Flask(__name__)

# Set up database access (MongoDB)
dbclient = MongoClient()
db = dbclient.wot
# Get the thing collection
thingscollection = db.thing.find()
# Create JSON-data from collection via a Python list
thingslist = list(thingscollection)
things = dumps(thingslist)

# Set up subscription handler
subscriptions = Subscriptions()

# Helper function to convert Mongo object(s) to JSON
def toJson(data):
    return dumps(data)


@app.route("/")
def index():
    return render_template("index.html")


# GET list of thing descriptions
@app.route('/things', methods=['GET'])
def get_things():
    return things


# GET thing description
@app.route('/things/<name>', methods=['GET'])
def get_thing(name):
    thing = db.thing.find({"name": name})
    if thing.count() <= 0:
        return '{"Error:": "No such name"}'
    return toJson(thing)


# GET list of actors for named thing
@app.route('/things/<name>/actors', methods=['GET'])
def get_thingactors(name):
    thing = db.thing.find({"name": name})
    if thing.count() <= 0:
        return '{"Error:": "No such name"}'
    for data in thing:
        thing_dict = json.loads(toJson(data))
    return toJson(thing_dict['actors'])


# GET list of sensors for named thing
@app.route('/things/<name>/sensors', methods=['GET'])
def get_thingsensors(name):
    thing = db.thing.find({"name": name})
    if thing.count() <= 0:
        return '{"Error:": "No such name"}'
    for data in thing:
        thing_dict = json.loads(toJson(data))
    return toJson(thing_dict['sensors'])

# POST (set) value for thing actor
@app.route('/things/<name>/<actor>/<value>', methods=['POST'])
def set_thingactor(name, actor, value):
    thing = db.thing.find({"$and": [{"name": name}, {"actors.name": actor}]})
    if thing.count() <= 0:
        return '{"Error:": "No such name"}'
    for data in thing:
        thing_dict = json.loads(toJson(data))
        for item in thing_dict['actors']:
            if item['name'] == actor:
                post_url = item['uri']
                if not post_url.endswith("/"):
                    post_url += "/" + str(value)
                else:
                    post_url += str(value)
        response = requests.post(post_url)
    return response.text


# GET value for thing sensor
@app.route('/things/<name>/<sensor>', methods=['GET'])
def get_thingsensor(name, sensor):
    thing = db.thing.find({"$and": [{"name": name}, {"sensors.name": sensor}]})
    if thing.count() <= 0:
        return '{"Error:": "No such name"}'
    for data in thing:
        thing_dict = json.loads(toJson(data))
        for item in thing_dict['sensors']:
            if item['name'] == sensor:
                get_url = item['uri']
        response_in = requests.get(get_url)
        response_out = Response(response_in.text)
        response_out.headers['Content-Type'] = "application/json"
    return response_out


########################################
# Routes to handle subscriptions
# (as pubsub-model using HTML5 SSE)
########################################
@app.route("/things/<name>/subscriptions")
def debug(name):
    # TODO: implement subscriptions for specific things
    return "Currently %d subscriptions" % subscriptions.num_subscriptions()


@app.route("/things/publish", methods=['POST'])
def publish():
    # Send dummy data
    msg = request.get_data()
    print msg
    # TODO: Implement publish for specific things
    def notify():
        for sub in subscriptions.get_subscriptions()[:]:
            sub.put(msg)

    gevent.spawn(notify)
    return Response(msg, mimetype="application/json")


@app.route("/things/<name>/subscribe")
def subscribe(name):
    def gen():
        q = Queue()
        subscriptions.add_subscription(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit:  # Or maybe use flask signals
            subscriptions.remove_subscription(q)

    return Response(gen(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.debug = True
    server = WSGIServer(("0.0.0.0", 5000), app)
    server.serve_forever()