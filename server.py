from flask import Flask
from flask import request, redirect
from flask import jsonify
from flask import render_template
from flask import send_file
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import json
import hashlib
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)
client = MongoClient(port=27017)
db=client.user
Order=client.order


tomato_pic = "https://choosemyplate-prod.azureedge.net/sites/default/files/styles/food_gallery_colorbox__800x500_/public/myplate/Tomatoes.jpeg?itok=LEvJrg7y"
carrot_pic = "https://www.hindimeaning.com/wp-content/uploads/2012/12/carrots-vegetables.jpg"
potato_pic = "https://www.healthline.com/hlcmsresource/images/topic_centers/Food-Nutrition/high-protein-veggies/388x210_potatoes.jpg"
cucumber_pic = "https://www.hindimeaning.com/wp-content/uploads/2015/08/cucumbers.jpg"
broccoli_pic = "https://cdn.pixabay.com/photo/2016/03/05/19/02/broccoli-1238250__340.jpg"
peas_pic = "https://www.johnnyseeds.com/dw/image/v2/BBBW_PRD/on/demandware.static/-/Sites-jss-master/default/dw52d854a2/images/products/vegetables/03874_01_cosmos.jpg?sw=387&cx=302&cy=0&cw=1196&ch=1196"
cabbage_pic = "https://www.hindimeaning.com/wp-content/uploads/2012/12/green-cabbage.jpg"
onion_pic = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgqu6hdRXn-NjRRA_8Brgw05QHXNHZVrCLb6EQKtM3E_1MHMPr"


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/login.html', methods=['GET','POST'])
def login():
	print("index returned")
	out={}
	out = request.args.get('out')
	if(out=='1'):
		out={'You have logged out successfully.':1}
	else:
		out={}
	print(out)
	return render_template('login.html',out=out)

@app.route('/forgotPassword.html', methods=['GET','POST'])
def forgot_pass():
	return render_template('forgotPassword.html')


@app.route('/main_page.html', methods=['GET','POST'])
def main():
	userId = request.args.get('id')
	print(userId)
	print("index returned")
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	for key,value in orders.items():
		if key=='tomato' :
			price += (value*39.90)
		elif key=='carrot' :
			price += (value*19.50)
		elif key=='potato' :
			price += (value*32.20)
		elif key=='cucumber' :
			price += (value*59.90)
		elif key=='broccoli' :
			price += (value*79.90)
		elif key=='peas' :
			price += (value*59.90)
		elif key=='cabbage' :
			price += (value*15.90)
		elif key=='onion' :
			price += (value*43.99)
	return render_template('main_page.html',main=userId, quantity =len(orders),price = '₹ '+str(price))

@app.route('/object_id', methods=['GET','POST'])
def object_id():
	print("Here")
	userEmail = request.form['email']
	userPassword = request.form['pass']
	encoded_password = hashlib.sha512(userPassword.encode()).hexdigest()
	print(userEmail)
	print(userPassword)
	print(encoded_password)
	ret_query = db.info.find_one({'email': userEmail})
	print("XXXXX")
	print(ret_query['_id'])
	try :
		if ret_query['password'] == encoded_password :
			return redirect('main_page.html?id='+str(ret_query['_id']))
		else :
			#return render_template('index_wrong_pass.html')
			return render_template('login.html',out={"Entered password is wrong":0})
			#return "Wrong Password"
	except TypeError:
		return "User not recognized \n Try to Sign Up."
	#return "Fuck Off"

@app.route('/signup.html', methods=['GET','POST'])
def signup():

	return render_template('signup.html')

@app.route('/handle_signup', methods=['POST'])
def handle_signup():
	print("Here23")
	userName = request.form['name']
	userEmail = request.form['email']
	userPhone = request.form['ph_number']
	userPassword = request.form['pass']
	userConfirmPassword = request.form['con_pass']
	encodedPassword = hashlib.sha512(userPassword.encode()).hexdigest()

	if(userPassword!=userConfirmPassword):
		return "Password does not match"
	else :
		print(userName)
		print(userPhone)
		print(userEmail)
		print(userPassword)
		print(encodedPassword)

		counter = 0
		entry = {
			'name' : userName,
			'password' : encodedPassword,
			'email' : userEmail,
			'phone' : userPhone,
		}


		for x in db.info.find({},{"_id": 0, "email": 1 }):
			if((x['email'])== entry['email']) :
				counter = 1
				break

		if counter==0 :
			result=db.info.insert_one(entry)
			for x in db.info.find({},{"_id": 0, "email": 1}):
				if(x['email']==userEmail):
					result = x['_id']
					break
			return redirect('main_page.html?id='+str(result))
		else :
			print('Error')

	return render_template('signup.html')

	
@app.route('/forgot_password', methods=['POST'])
def forgot_password():
	userEmail = request.form['email']
	userPhone = request.form['phone']
	counter=0

	for x in db.info.find({},{"_id": 0, "email": 1, "phone":1, "name":1 }):
		if((x['email'])==userEmail and x['phone']==userPhone) :
			counter = 1
			break

	if(counter==1):
		import smtplib
		import random
		import string

		gmail_user = 'thella.wala@gmail.com'  
		gmail_password = 'Rahul@idea'
		gmail_reciever = x['email']
		user_name = x['name']
		temp_pass = ''
		for i in range(7) :
			temp_pass += random.choice(string.ascii_letters)

		SUBJECT = 'Temporary Password Recovery'
		TEXT = 'Dear '+user_name+',\n\nA request to reset the password for your account has been made. \nYour temporary password is '+temp_pass+'\nPlease change it after your first login.\n\nRegards-\nTeam Thella wala.'
		message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

		mail = smtplib.SMTP('smtp.gmail.com',587)
		mail.ehlo()
		mail.starttls()
		mail.login(gmail_user, gmail_password)
		mail.sendmail(gmail_user,gmail_reciever, message)
		myquery = { "email": gmail_reciever }
		newvalues = { "$set" : {"password": hashlib.sha512(temp_pass.encode()).hexdigest() }}

		x = db.info.update_one(myquery, newvalues)
		for x in db.info.find():
			print(x)
		mail.close()

	else :
		return "Email/Phone Number not found."

	return render_template('login.html')


@app.route('/clear_cart', methods=['GET','POST'])
def clear_cart():
	userId = request.args.get('id')
	print(userId)
	invalid ={"Your Cart is Empty":1}
	orders = {}
	myquery = { "Customer_Id": userId }
	newvalues = { "$set" : {"Order": orders }}
	db.cart.update_one(myquery, newvalues)
	return render_template('cart.html',invalid=invalid, open_cart=orders, main=userId)


@app.route('/open_cart', methods=['GET','POST'])
def open_cart():
	userId = request.args.get('id')
	print(userId)
	dicti={}
	
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	for key,value in orders.items():
		arr = [] #pic,price,quantity
		if key=='tomato' :
			arr.append(tomato_pic)
			arr.append(39.90)
			price += (value*39.90)
		elif key=='carrot' :
			arr.append(carrot_pic)
			arr.append(19.50)
			price += (value*19.50)
		elif key=='potato' :
			arr.append(potato_pic)
			arr.append(32.20)
			price += (value*32.20)
		elif key=='cucumber' :
			arr.append(cucumber_pic)
			arr.append(59.90)
			price += (value*59.90)
		elif key=='broccoli' :
			arr.append(broccoli_pic)
			arr.append(79.90)
			price += (value*79.90)
		elif key=='peas' :
			arr.append(peas_pic)
			arr.append(59.90)
			price += (value*59.90)
		elif key=='cabbage' :
			arr.append(cabbage_pic)
			arr.append(15.90)
			price += (value*15.90)
		elif key=='onion' :
			arr.append(onion_pic)
			arr.append(43.99)
			price += (value*43.99)
		arr.append(value)
		arr.append(arr[-2]*arr[-1])
		dicti[key] = arr
	print(dicti)
	if(len(dicti)==0) :
		invalid ={"Your Cart is Empty":1}
	else:
		invalid = {}
	#dicti = {'carrot':[50,18.00],'tomato':[30,14.00]}
	return render_template('cart.html',open_cart=dicti, main=userId, invalid=invalid, quantity =len(dicti),price = '₹ '+str(price))

@app.route('/add_tomato', methods=['GET','POST'])
def add_tomato():
	userId = request.args.get('id')
	print(userId)
	print('XXXXXXXXXXXXXXXXXXX')
	counter=0
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			if 'tomato' in orders.keys():
				orders['tomato'] += 1
			else :
				orders['tomato'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	if(counter==0) :
		orders = {"tomato":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)

@app.route('/add_carrot', methods=['GET','POST'])
def add_carrot():
	counter=0
	userId = request.args.get('id')
	print(userId)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			if 'carrot' in orders.keys():
				orders['carrot'] += 1
			else :
				orders['carrot'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	if(counter==0) :
		orders = {"carrot":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)

@app.route('/add_potato', methods=['GET','POST'])
def add_potato():
	counter=0
	userId = request.args.get('id')
	print(userId)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			if 'potato' in orders.keys():
				orders['potato'] += 1
			else :
				orders['potato'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	if(counter==0) :
		orders = {"potato":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)

@app.route('/add_cucumber', methods=['GET','POST'])
def add_cucumber():
	counter=0
	userId = request.args.get('id')
	print(userId)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			if 'cucumber' in orders.keys():
				orders['cucumber'] += 1
			else :
				orders['cucumber'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	print(orders)
	if(counter==0) :
		orders = {"cucumber":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)

@app.route('/add_broccoli', methods=['GET','POST'])
def add_broccoli():
	counter=0
	userId = request.args.get('id')
	print(userId)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			if 'broccoli' in orders.keys():
				orders['broccoli'] += 1
			else :
				orders['broccoli'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	if(counter==0) :
		orders = {"broccoli":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)
	
@app.route('/add_peas', methods=['GET','POST'])
def add_peas():
	counter=0
	userId = request.args.get('id')
	print(userId)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			if 'peas' in orders.keys():
				orders['peas'] += 1
			else :
				orders['peas'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	if(counter==0) :
		orders = {"peas":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)

@app.route('/add_cabbage', methods=['GET','POST'])
def add_cabbage():
	counter=0
	userId = request.args.get('id')
	print(userId)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			if 'cabbage' in orders.keys():
				orders['cabbage'] += 1
			else :
				orders['cabbage'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	if(counter==0) :
		orders = {"cabbage":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)

@app.route('/add_onion', methods=['GET','POST'])
def add_onion():
	counter=0
	userId = request.args.get('id')
	print(userId)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			print(x['Order'])
			orders = x['Order']
			if 'onion' in orders.keys():
				orders['onion'] += 1
			else :
				orders['onion'] = 1
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			counter = 1
			break
	if(counter==0) :
		orders = {"onion":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return redirect('main_page.html?id='+userId)

@app.route('/blog.html', methods=['GET','POST'])
def blog():
	userId = request.args.get('id')
	print(userId)
	return render_template('blog.html',main=userId)

@app.route('/previous_order', methods=['GET','POST'])
def previous_order():
	userId = request.args.get('id')
	print(userId)
	order_history = {}
	counter = 0
	for x in Order.order.find({},{"_id": 1, "UserId": 1, "Date":1, "Time":1, "Order":1 }):
		if((x['UserId'])=='userName') :
			temp_history = {}
			temp_history['Invoice'] = x['_id']
			temp_history['Date'] = x['Date']
			temp_history['Time'] = x['Time']
			temp_order = x['Order']
			for key,value in temp_order.items():
				if key=='tomato' :
					value.append(tomato_pic)
					value.append(value[0]*value[1])
				elif key=='carrot' :
					value.append(carrot_pic)
					value.append(value[0]*value[1])
				elif key=='potato' :
					valuearr.append(potato_pic)
					value.append(value[0]*value[1])
				elif key=='cucumber' :
					value.append(cucumber_pic)
					value.append(value[0]*value[1])
				elif key=='broccoli' :
					value.append(broccoli_pic)
					value.append(value[0]*value[1])
				elif key=='peas' :
					value.append(peas_pic)
					value.append(value[0]*value[1])
				elif key=='cabbage' :
					value.append(cabbage_pic)
					value.append(value[0]*value[1])
				elif key=='onion' :
					value.append(onion_pic)
					value.append(value[0]*value[1])
			temp_history['Order'] = temp_order
			order_history[counter] = temp_history
			counter+=1

	print(order_history)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	for key,value in orders.items():
		if key=='tomato' :
			price += (value*39.90)
		elif key=='carrot' :
			price += (value*19.50)
		elif key=='potato' :
			price += (value*32.20)
		elif key=='cucumber' :
			price += (value*59.90)
		elif key=='broccoli' :
			price += (value*79.90)
		elif key=='peas' :
			price += (value*59.90)
		elif key=='cabbage' :
			price += (value*15.90)
		elif key=='onion' :
			price += (value*43.99)

	return render_template('orders.html',previous_order=order_history,main=userId, quantity =len(orders),price = '₹ '+str(price))

@app.route('/pending_order', methods=['GET','POST'])
def pending_order():
	userId = request.args.get('id')
	print(userId)
	invalid = {"Your have no Pending order":1}
	dicti = {}
	counter = 0
	for x in Order.pending.find({},{"_id": 1, "User_Id": 1, "Status":1, "Delivery":1, "Price":1, "Time":1, "Order":1}):
		if((x['User_Id'])==userId and x['Status']!='Order Cancel') :
			dicti[counter] = x
			counter+=1
			invalid = {}
	print(dicti)
	print("yyyyyyyyyyyyyy")

	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	for key,value in orders.items():
		if key=='tomato' :
			price += (value*39.90)
		elif key=='carrot' :
			price += (value*19.50)
		elif key=='potato' :
			price += (value*32.20)
		elif key=='cucumber' :
			price += (value*59.90)
		elif key=='broccoli' :
			price += (value*79.90)
		elif key=='peas' :
			price += (value*59.90)
		elif key=='cabbage' :
			price += (value*15.90)
		elif key=='onion' :
			price += (value*43.99)

	return render_template('pending_order.html',pending_order=dicti,main=userId,invalid=invalid, quantity =len(orders),price = '₹ '+str(price))

@app.route('/checkout', methods=['GET','POST'])
def checkout():
	userId = request.args.get('id')
	print(userId)

	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	for key,value in orders.items():
		if key=='tomato' :
			price += (value*39.90)
		elif key=='carrot' :
			price += (value*19.50)
		elif key=='potato' :
			price += (value*32.20)
		elif key=='cucumber' :
			price += (value*59.90)
		elif key=='broccoli' :
			price += (value*79.90)
		elif key=='peas' :
			price += (value*59.90)
		elif key=='cabbage' :
			price += (value*15.90)
		elif key=='onion' :
			price += (value*43.99)

	if price>150 :
		shipping = 'Free'
		total = price
	else:
		shipping = '₹ '+str(50)
		total = price+50

	return render_template('checkout.html',main=userId,order=['₹ '+str(price),shipping,'₹ '+str(total)])

@app.route('/place_order', methods=['GET','POST'])
def place_order():
	import datetime

	userId = request.args.get('id')
	print(userId)
	dicti={}
	
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	for key,value in orders.items():
		arr = [] #pic,price,quantity
		if key=='tomato' :
			arr.append(tomato_pic)
			arr.append(39.90)
			price += (value*39.90)
		elif key=='carrot' :
			arr.append(carrot_pic)
			arr.append(19.50)
			price += (value*19.50)
		elif key=='potato' :
			arr.append(potato_pic)
			arr.append(32.20)
			price += (value*32.20)
		elif key=='cucumber' :
			arr.append(cucumber_pic)
			arr.append(59.90)
			price += (value*59.90)
		elif key=='broccoli' :
			arr.append(broccoli_pic)
			arr.append(79.90)
			price += (value*79.90)
		elif key=='peas' :
			arr.append(peas_pic)
			arr.append(59.90)
			price += (value*59.90)
		elif key=='cabbage' :
			arr.append(cabbage_pic)
			arr.append(15.90)
			price += (value*15.90)
		elif key=='onion' :
			arr.append(onion_pic)
			arr.append(43.99)
			price += (value*43.99)
		arr.append(value)
		arr.append(arr[-2]*arr[-1])
		dicti[key] = arr

	status = 'Order Pending'
	delivery = 'NA'
	d = datetime.datetime.now()

	entry = { 	'User_Id' : userId,
				'Status' : status,
				'Delivery' : delivery,
				'Price' : price,
				'Time' : d,
				'Order' : dicti
	}

	Order.pending.insert_one(entry)

	orders = {}
	myquery = { "Customer_Id": userId }
	newvalues = { "$set" : {"Order": orders }}
	db.cart.update_one(myquery, newvalues)

	return render_template('main_page.html',main=userId)

@app.route('/cancel_order', methods=['GET','POST'])
def cancel_order():
	print("SSSSSSSSSSSS")
	userId = request.args.get('id')
	print(userId)
	orderId = request.args.get('order_id')
	print(orderId)
	#a = Order.pending.delete_many({'_id': orderId})
	#print(a)

	myquery = { "_id": ObjectId(orderId)}
	newvalues = { "$set" : {"Status": 'Order Cancel' }}
	a = Order.pending.update_one(myquery, newvalues)
	print(a)
	invalid = {"Your have no Pending order":1}
	dicti = {}
	counter = 0
	for x in Order.pending.find({},{"_id": 1, "User_Id": 1, "Status":1, "Delivery":1, "Price":1, "Time":1, "Order":1}):
		if((x['User_Id'])==userId and x['Status']!='Order Cancel') :
			dicti[counter] = x
			counter+=1
			invalid = {}
	#print(dicti)
	#print("yyyyyyyyyyyyyy")


	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	for key,value in orders.items():
		if key=='tomato' :
			price += (value*39.90)
		elif key=='carrot' :
			price += (value*19.50)
		elif key=='potato' :
			price += (value*32.20)
		elif key=='cucumber' :
			price += (value*59.90)
		elif key=='broccoli' :
			price += (value*79.90)
		elif key=='peas' :
			price += (value*59.90)
		elif key=='cabbage' :
			price += (value*15.90)
		elif key=='onion' :
			price += (value*43.99)

	return render_template('pending_order.html',pending_order=dicti,main=userId,invalid=invalid, quantity =len(orders),price = '₹ '+str(price))
