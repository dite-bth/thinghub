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
    'api_doc': u'http://10.0.0.3:8080/api/doc#lightmanager',
    'description': u'Manages sensors and actuators to control lights',
    'sensors':[{
        'id': 1,
        'uri': u'http://10.0.0.3:8080/lightmanager/luminosity1',
        'method': u'GET',
        'name': u'Luminosity sensor1',
        'description': u'Current luminosity for sensor 1 (measured in 5 minute intervals)',
        'type': u'Float',
        'value': 0.675
        }],
    'actors':[
        {
        'id': 1,
        'uri': u'http://10.0.0.3:8080/lightmanager/light1',
        'method': u'POST',
        'name': u'Window spot',
        'description': u'Lightswitch to control window spot',
        'type': u'Boolean',
        'value': u'False'},
        {
        'id': 2,
        'uri': u'http://10.0.0.3:8080/lightmanager/light2',
        'method': u'POST',
        'name': u'Roof ambient',
        'description': u'Lightswitch to control roof ambient',
        'type': u'Boolean',
        'value': u'False'}
    ]
  },
    {
        'id': 1,
        'name': u'Temperature manager',
        'uri': u'http://10.0.0.3:8080/tempmanager',
        'api_doc': u'http://10.0.0.3:8080/api/doc#tempmanager',
        'description': u'Manages thermometors and a thermostat to check and adjust the temperature',
        'sensors': [{
            'id': 1,
            'uri': u'http://10.0.0.3:8080/tempmanager/temperature-inside',
            'method': u'GET',
            'name': u'Temp inside',
            'description': u'Current temperature indoors in degrees Celsius (measured in 5 minute intervals)',
            'type': u'Float',
            'value': 23.45
            },
            {
                'id': 2,
                'uri': u'http://10.0.0.3:8080/tempmanager/temperature-outside',
                'method': u'GET',
                'name': u'Temp outside',
                'description': u'Current temperature outdoors in degrees Celsius (measured in 5 minute intervals)',
                'type': u'Float',
                'value': 11.15
            }
        ],
        'actors': [
            {
                'id': 1,
                'uri': u'http://10.0.0.3:8080/tempmanager/thermostat',
                'method': u'POST',
                'name': u'Thermostat',
                'description': u'Use to set setpoint temperature (degrees Celsius)',
                'type': u'Float',
                'value': u'23.5'}
        ]
    }
]

result = db.thing.insert_many(initial_things)
print result.inserted_ids
