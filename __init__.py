# -*- coding: utf-8 -*-
import threading, time, subprocess

#MongoDB
import json, requests, gevent
from bson.json_util import dumps
from pymongo import MongoClient

#Flask
from flask import Flask, render_template, Response, request, jsonify
from gevent.wsgi import WSGIServer
from gevent.queue import Queue
from sse import ServerSentEvent
from subscriptions import Subscriptions
from httperrors import  UsageError
app = Flask(__name__)
app.debug = False
flaskServer = WSGIServer(("127.0.0.1", 5000), app)

#CoAP server
from coapserver import CoAPServer
coapServer = CoAPServer("0.0.0.0", 5683)


# Set up database access (MongoDB)
db_client = MongoClient()
db = db_client.wot

# Set up subscription handler
subscriptions = Subscriptions()


########################################################
#  Helper functions
########################################################
# Convert MongoDB to JSON
def to_json(data):
    return dumps(data)


# Validation function to ensure proper Thing description format
def validate_thing_description(thing_description):
    try:
        mandatory_keys = ('name', 'uri', 'description', 'api_doc', 'actors', 'sensors')
        mandatory_sub_keys = ('name', 'uri', 'description', 'type', 'value', 'method')
        # Also need to check len() because all() returns True for empty iterable
        if len(thing_description) > 0 and not all(k in thing_description for k in mandatory_keys):
            return False
        if len(thing_description['actors']) > 0:
            for actor in thing_description['actors']:
                if not all(k in actor for k in mandatory_sub_keys):
                    return False
        if len(thing_description['sensors']) > 0:
            for sensor in thing_description['sensors']:
                if not all(k in sensor for k in mandatory_sub_keys):
                    return False
        return True
    except:
        raise ValueError


#######################################################
# Set up route for error handling using a HTTP-error
# class to define and raise specific errors
#######################################################
@app.errorhandler(UsageError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


#######################################################
# Main routes for the service
#######################################################
@app.route("/")
def index():
    # Get the thing collection
    things_collection = db.thing.find()
    things_list = list(things_collection)
    return render_template("index.html", things=things_list)


# Endpoint for registering devices
@app.route("/register", methods=['POST'])
def register():
    try:
        # Get Thing description POST data and convert to JSON
        data = json.loads(request.get_data())

        # Validate Thing description
        if validate_thing_description(data):
            return Response('{"Success": "Registered"}', mimetype='application/json')
        else:
            raise UsageError('Malformed Thing description', status_code=400)
    except ValueError:
        raise UsageError('Malformed JSON', status_code=400)


# GET list of thing descriptions
@app.route('/things', methods=['GET'])
def get_things():
    # Get the thing collection
    things_collection = db.thing.find()
    # Create JSON-data from collection via a Python list
    things_list = list(things_collection)
    things = dumps(things_list)
    return things


# GET thing description
@app.route('/things/<name>', methods=['GET'])
def get_thing(name):
    thing = db.thing.find({"name": name})
    if thing.count() <= 0:
        raise UsageError("No such thing (name)", status_code=400)
        return None
    return to_json(thing)


# GET list of actors for named thing
@app.route('/things/<name>/actors', methods=['GET'])
def get_thingactors(name):
    thing = db.thing.find({"name": name})
    if thing.count() <= 0:
        raise UsageError("No such thing (name)", status_code=400)
        return None
    for data in thing:
        thing_dict = json.loads(to_json(data))
    return to_json(thing_dict['actors'])


# GET list of sensors for named thing
@app.route('/things/<name>/sensors', methods=['GET'])
def get_thingsensors(name):
    thing = db.thing.find({"name": name})
    if thing.count() <= 0:
        raise UsageError("No such thing (name)", status_code=400)
        return None
    for data in thing:
        thing_dict = json.loads(to_json(data))
    return to_json(thing_dict['sensors'])


# POST (set) value for thing actor
@app.route('/things/<name>/<actor>/<value>', methods=['POST'])
def set_thingactor(name, actor, value):
    thing = db.thing.find({"$and": [{"name": name}, {"actors.name": actor}]})
    if thing.count() <= 0:
        raise UsageError("No such thing (name)", status_code=400)
        return None
    for data in thing:
        thing_dict = json.loads(to_json(data))
        for item in thing_dict['actors']:
            if item['name'] == actor:
                post_url = item['uri']
                payload = '{"value": "%s"}' % value
                try:
                    response = requests.post(post_url, data=payload, timeout=8)
                except requests.exceptions.Timeout:
                    #Request timed out
                    raise UsageError("Request timed out for %s" % post_url, status_code=408)
                except requests.exceptions.RequestException as e:
                    # Something went really wrong...
                    raise UsageError(e.message, status_code=503)
                else:
                    return response.text
            else:
                raise UsageError("No such actor (name)", status_code=400)


# GET value for thing sensor
@app.route('/things/<name>/<sensor>', methods=['GET'])
def get_thingsensor(name, sensor):
    thing = db.thing.find({"$and": [{"name": name}, {"sensors.name": sensor}]})
    if thing.count() <= 0:
        raise UsageError("No such thing (name)", status_code=400)
        return None
    for data in thing:
        thing_dict = json.loads(to_json(data))
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
    # TODO: implement subscriptions for specific things
    print("Subscription added")
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


def initFlask():
    try:
        print "Starting Flask server..."
        flaskServer.serve_forever()
    except KeyboardInterrupt:
        print "Stopping flask server"
        flaskServer.close()

def initCoAP():
    try:
        print "Starting CoAP server..."
        coapServer.listen(10)
    except KeyboardInterrupt:
        coapServer.close()


if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()

    threads = []
    flask_thread = threading.Thread(target=initFlask)
    flask_thread.daemon = True
    threads.append(flask_thread)
    coap_thread = threading.Thread(target=initCoAP)
    coap_thread.daemon = True
    threads.append(coap_thread)

    for thread in threads:
        thread.start()

    # TODO: add more servers
    # For now: just loop and sleep until CTRL+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Server shutdown initiated..."