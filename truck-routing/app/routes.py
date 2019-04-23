from app import api_config
from app import app
from flask import request
from time import sleep
import requests

# replace with requests.get(PARAMS)
def stringifyTuple(tup):
    return str(tup).replace(' ','').replace('(','').replace(')','')


# to run sorted(key=fn)
def fn(obj):
    return obj['duration']['value']


@app.route('/', methods = ['POST'])
@app.route('/index')
def index():

    truck1 = (28.552176, 77.555084)
    truck2 = (28.482101, 77.530849)
    truck3 = (28.607810, 77.227598)
    truck4 = (28.633607, 77.464839)
    trucks = list()
    trucks.append(truck1)
    trucks.append(truck2)
    trucks.append(truck3)
    trucks.append(truck4)

    coords = request.get_json()
    address = request.get_data()
    
    if coords is None:
        url = 'https://maps.googleapis.com/maps/api/geocode/json?' + address + '&key=api_config.apiKey'
        orderLocationData = requests.get(url).json()
        order = (orderLocationData['results'][0]['geometry']['location']['lat'],
                 orderLocationData['results'][0]['geometry']['location']['lng'])
    else:
        order = (coords['latitude'], coords['longitude'])
    
    # url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=&destinations=&key='
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='

    url = url + stringifyTuple(order) + '&destinations=';
    for truck in trucks:  
        url = url + stringifyTuple(truck) + '|'
    url = url[:-1] + '&key=' + api_config.apiKey
    # print(url)

    data = requests.get(url).json()
    print(data)

    realTrucks = list()

    for index, datarow in enumerate(data['rows'][0]['elements']):
        datarow['truck_location'] = data['destination_addresses'][index]
        realTrucks.append(datarow)

    realTrucks = sorted(realTrucks, key=fn)
    print(realTrucks)
    return '200';