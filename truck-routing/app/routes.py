from app import config
from app import app
from flask import request
from time import sleep
import requests
import pymongo

# replace with requests.get(PARAMS)
def stringifyTuple(tup):
    return str(tup).replace(' ','').replace('(','').replace(')','')


def querifyString(str):
    return str.replace(' ','+')


def getOrderLocation(address):

    # if coords is None:
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + config.apiKey
    print(url)
    orderLocationData = requests.get(url).json()
    order = (orderLocationData['results'][0]['geometry']['location']['lat'],
                orderLocationData['results'][0]['geometry']['location']['lng'])
    # else:
    #     order = (coords['latitude'], coords['longitude'])
    
    print(order)
    return order


# to run sorted(key=fn)
def fn(obj):
    return obj['duration']['value']


def truckRoute(data, order, db):
    # list of trucks
    realTrucks = list()
    # append order_location. used to update the trucker's DOM
    for index, datarow in enumerate(data['rows'][0]['elements']):
        datarow['truck_location'] = data['destination_addresses'][index]
        datarow['order_location'] = {
                                        'lat': str(order[0]),
                                        'lng': str(order[1])
                                    } 
        realTrucks.append(datarow)

    # get the fastest truck and its index
    assignedTruck = min(realTrucks, key=fn)
    assignedTruckIndex = realTrucks.index(assignedTruck)
    
    # resets the cursor back to the beginning of the collection
    dbTrucks = db.trucks.find()
    
    # update the appropriate truck document's orderList
    assignedTruckID = dbTrucks[assignedTruckIndex]['_id']
    updateCriteria = {'_id': assignedTruckID}
    updatedValues = {'$push': { 'orderList': assignedTruck }}
    db.trucks.update(updateCriteria, updatedValues)


@app.route('/', methods = ['POST'])
@app.route('/index')
def index():

    # initialise database
    client = pymongo.MongoClient('localhost',config.mongoDBPORT)
    db = client['Thellawala']
    dbTrucks = db.trucks.find()

    coords = request.get_json()
    address = request.get_data().decode("utf-8") 
    address = querifyString(address)
    
    # if the html5 geolocation api does not return coords,
    # instead if an address is passed
    # convert address into coordinates
    if coords is None:
        order = getOrderLocation(address)
    else:
        order = (coords['latitude'], coords['longitude'])

    # prepare distance matrix api query
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='
    url = url + stringifyTuple(order) + '&destinations=';
    for truck in dbTrucks:
        location = (float(truck['location']['lat']), float(truck['location']['lng']))
        print(location)
        url = url + stringifyTuple(location) + '|'
    url = url[:-1] + '&key=' + config.apiKey
    print(url)
    # finish manipulating url with the order location

    # query the distance matrix api
    data = requests.get(url).json()
    truckRoute(data, order, db)
    
    return '200';

# @app.route('/trucker', methods = ['GET'])
# # the truckers url
# def trucker():
    
    