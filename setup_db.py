# -*- coding: utf-8 -*-
from pymongo import MongoClient

# Set up initial test database (MongoDB)
dbclient = MongoClient()
db = dbclient.wot
# Set up an initial things collection
initial_things = [
    {
    'id': 1,
    'name': u'Light manager',
    'uri': u'http://10.0.0.3:8080/lightmanager',
    'api_doc': u'http://10.0.0.3:8080/api/doc',
    'description': u'Manages sensors and actuators to control lights',
    'sensors':[{
        'id': 1,
        'uri': u'http://10.0.0.3:8080/lightmanager/luminosity1',
        'methods': u'GET',
        'name': u'Luminosity sensor1',
        'description': u'Current luminosity for sensor 1 (measured in 5 minute intervals)',
        'type': u'Float',
        'value': 0.675
        }],
    'actors':[{
        'id': 1,
        'uri': u'http://10.0.0.3:8080/lightmanager/light1',
        'methods': u'POST',
        'name': u'Light1',
        'description': u'Lightswitch to control light 1',
        'type': u'Boolean',
        'value': u'False'
    }]
  }
]

result = db.thing.insert_many(initial_things)
print result.inserted_ids
