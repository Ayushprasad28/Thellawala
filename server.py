from flask import Flask
from flask import request, redirect
from flask import jsonify
from flask import render_template
from flask import send_file
from flask_cors import CORS
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import json
import hashlib
from pymongo import MongoClient
from bson.objectid import ObjectId
from twilio.rest import Client
import smtplib
from app import routes

app = Flask(__name__)
CORS(app)



mongo = MongoClient(port=27017)
db=mongo.user
Order=mongo.order


tomato_pic = "https://choosemyplate-prod.azureedge.net/sites/default/files/styles/food_gallery_colorbox__800x500_/public/myplate/Tomatoes.jpeg?itok=LEvJrg7y"
carrot_pic = "https://www.hindimeaning.com/wp-content/uploads/2012/12/carrots-vegetables.jpg"
potato_pic = "https://www.healthline.com/hlcmsresource/images/topic_centers/Food-Nutrition/high-protein-veggies/388x210_potatoes.jpg"
cucumber_pic = "https://www.hindimeaning.com/wp-content/uploads/2015/08/cucumbers.jpg"
broccoli_pic = "https://cdn.pixabay.com/photo/2016/03/05/19/02/broccoli-1238250__340.jpg"
peas_pic = "https://www.johnnyseeds.com/dw/image/v2/BBBW_PRD/on/demandware.static/-/Sites-jss-master/default/dw52d854a2/images/products/vegetables/03874_01_cosmos.jpg?sw=387&cx=302&cy=0&cw=1196&ch=1196"
cabbage_pic = "https://www.hindimeaning.com/wp-content/uploads/2012/12/green-cabbage.jpg"
onion_pic = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgqu6hdRXn-NjRRA_8Brgw05QHXNHZVrCLb6EQKtM3E_1MHMPr"


gmail_user = 'thella.wala@gmail.com'  
gmail_password = 'Rahul@idea' 	

if __name__ == '__main__':
	app.run(host='192.168.43.212',port=9999)


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


@app.route('/coming', methods=['GET','POST'])
def coming():
	userId= request.args.get('id')
	return render_template('ComingSoon.html',main=userId)

@app.route('/forgotPassword.html', methods=['GET','POST'])
def forgot_pass():
	return render_template('forgotPassword.html')


@app.route('/main_page.html', methods=['GET','POST'])
def main():
	userId = request.args.get('id')
	print(userId)
	print("index returned")
	orders ={}
	price=0
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break

	if(len(orders)>0) :
		for key,value in orders.items():
			if key=='tomato' :
				price += (value*39.90)
			elif key=='carrot' :
				price += (value*31.10)
			elif key=='potato' :
				price += (value*10.90)
			elif key=='cucumber' :
				price += (value*38.00)
			elif key=='broccoli' :
				price += (value*45.00)
			elif key=='peas' :
				price += (value*38.00)
			elif key=='cabbage' :
				price += (value*24.90)
			elif key=='onion' :
				price += (value*19.00)
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
			for x in db.info.find({},{"_id": 1, "email": 1}):
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

		gmail_reciever = x['email']
		user_name = x['name']
		temp_pass = ''
		for i in range(7) :
			temp_pass += random.choice(string.ascii_letters)

		SUBJECT = 'Temporary Password Recovery'
		TEXT = 'Dear '+user_name+',\n\nA request to reset the password for your account has been made. \nYour new password is '+temp_pass+'\n\nRegards-\nTeam Thella wala.'
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

	return render_template('login.html',out={})


@app.route('/clear_cart', methods=['GET','POST'])
def clear_cart():
	userId = request.args.get('id')
	print(userId)
	invalid ={"Your Cart is Empty":1}
	orders = {}
	myquery = { "Customer_Id": userId }
	newvalues = { "$set" : {"Order": orders }}
	db.cart.update_one(myquery, newvalues)
	return redirect('open_cart?id='+str(userId))
	#render_template('cart.html',invalid=invalid, button_open_cart=orders, main=userId)


@app.route('/open_cart', methods=['GET','POST'])
def open_cart():
	userId = request.args.get('id')
	print(userId)
	dicti={}
	
	orders={}
	
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
			arr.append(31.10)
			price += (value*31.10)
		elif key=='potato' :
			arr.append(potato_pic)
			arr.append(10.90)
			price += (value*10.90)
		elif key=='cucumber' :
			arr.append(cucumber_pic)
			arr.append(42.00)
			price += (value*42.00)
		elif key=='broccoli' :
			arr.append(broccoli_pic)
			arr.append(45.00)
			price += (value*45.00)
		elif key=='peas' :
			arr.append(peas_pic)
			arr.append(38.00)
			price += (value*38.00)
		elif key=='cabbage' :
			arr.append(cabbage_pic)
			arr.append(24.90)
			price += (value*24.90)
		elif key=='onion' :
			arr.append(onion_pic)
			arr.append(19.00)
			price += (value*19.00)
		arr.append(value)
		arr.append(arr[-2]*arr[-1])
		dicti[key] = arr
	print(dicti)
	b_cart={}
	
	if(len(dicti)==0) :
		invalid ={"Your Cart is Empty":1}
		b_cart = {}
	else:
		invalid = {}
		b_cart = {"Button":1}
	#dicti = {'carrot':[50,18.00],'tomato':[30,14.00]}
	return render_template('cart.html',open_cart=dicti, main=userId, button_cart =b_cart, invalid=invalid, quantity =len(dicti),price = '₹ '+str(price))

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
	invalid = {"Your have no Previous Orders":1}
	order_history = {}
	counter = 0
	for x in Order.order.find({},{"_id": 1, "UserId": 1, "Invoice":1, "Date":1, "Time":1, "Price":1, "Order":1 }):
		if((x['UserId'])==userId) :
			order_history[counter] = x
			counter+=1
			invalid = {}

	print(order_history)
	orders={}
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0
	if(len(orders)>0) :
		for key,value in orders.items():
			if key=='tomato' :
				price += (value*39.90)
			elif key=='carrot' :
				price += (value*31.10)
			elif key=='potato' :
				price += (value*10.90)
			elif key=='cucumber' :
				price += (value*42.00)
			elif key=='broccoli' :
				price += (value*45.00)
			elif key=='peas' :
				price += (value*38.00)
			elif key=='cabbage' :
				price += (value*24.90)
			elif key=='onion' :
				price += (value*19.00)

	return render_template('orders.html',previous_order=order_history,main=userId, invalid=invalid, quantity =len(orders),price = '₹ '+str(price))

@app.route('/pending_order', methods=['GET','POST'])
def pending_order():
	userId = request.args.get('id')
	print(userId)
	invalid = {"Your have no Pending order":1}
	dicti = {}
	counter = 0
	for x in Order.pending.find({},{"_id": 1, "User_Id": 1, "Status":1, "Delivery":1, "Price":1, "Time":1, "Order":1}):
		if((x['User_Id']==userId) and (x['Status']!='Order Cancel') and (x['Status']!="Order Delivered")) :
			dicti[counter] = x
			counter+=1
			invalid = {}
			print(x)
	print(dicti)
	print("yyyyyyyyyyyyyy")

	orders = {}
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			print(orders)
			break
	price=0

	if(len(orders)>0):
		for key,value in orders.items():
			if key=='tomato' :
				price += (value*39.90)
			elif key=='carrot' :
				price += (value*31.10)
			elif key=='potato' :
				price += (value*10.90)
			elif key=='cucumber' :
				price += (value*42.00)
			elif key=='broccoli' :
				price += (value*45.00)
			elif key=='peas' :
				price += (value*38.00)
			elif key=='cabbage' :
				price += (value*24.90)
			elif key=='onion' :
				price += (value*19.00)

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
			price += (value*31.10)
		elif key=='potato' :
			price += (value*10.90)
		elif key=='cucumber' :
			price += (value*42.00)
		elif key=='broccoli' :
			price += (value*45.00)
		elif key=='peas' :
			price += (value*38.00)
		elif key=='cabbage' :
			price += (value*24.90)
		elif key=='onion' :
			price += (value*19.00)

	if price>99 :
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
			arr.append(31.10)
			price += (value*31.10)
		elif key=='potato' :
			arr.append(potato_pic)
			arr.append(10.90)
			price += (value*10.90)
		elif key=='cucumber' :
			arr.append(cucumber_pic)
			arr.append(42.00)
			price += (value*42.00)
		elif key=='broccoli' :
			arr.append(broccoli_pic)
			arr.append(45.00)
			price += (value*45.00)
		elif key=='peas' :
			arr.append(peas_pic)
			arr.append(38.00)
			price += (value*38.00)
		elif key=='cabbage' :
			arr.append(cabbage_pic)
			arr.append(24.90)
			price += (value*24.90)
		elif key=='onion' :
			arr.append(onion_pic)
			arr.append(19.00)
			price += (value*19.00)
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
			price += (value*31.10)
		elif key=='potato' :
			price += (value*10.90)
		elif key=='cucumber' :
			price += (value*42.00)
		elif key=='broccoli' :
			price += (value*45.00)
		elif key=='peas' :
			price += (value*38.00)
		elif key=='cabbage' :
			price += (value*24.90)
		elif key=='onion' :
			price += (value*19.00)

	return render_template('pending_order.html',pending_order=dicti,main=userId,invalid=invalid, quantity =len(orders),price = '₹ '+str(price))


@app.route('/authenticate.html', methods=['GET','POST'])
def authenticate():
	import random
	digits = "0123456789"
	OTP = "" 
	print("wwwwwwwww")
	userid = request.args.get('id')
	orderid =request.args.get('order_id')

	for x in Order.pending.find({},{"_id": 1, "Price":1}):
		if(x['_id']==ObjectId(orderid)) :
			price = x['Price']
  
	for i in range(4) : 
		OTP += digits[math.floor(random.random() * 10)] 
	OTP = str(OTP)
	print(OTP)
	encoded_OTP = hashlib.sha512(OTP.encode()).hexdigest()

	account_sid = 'ACe23d56343cab6c39c5a3b3a285361150'
	auth_token = 'dd9e600c8e0c6e878b8d049672681926'
	client = Client(account_sid, auth_token)

	
	mess = 'Total amount to be paid is Rs. '+str(price)+". After receiving the payment, please share the OTP for completion of your delivery. OTP : "+str(OTP)
	print(mess)

	message = client.messages.create(
                              from_='+17278975821',
                              body=mess,
                              to='+919910058241'
                          )

	print(message.sid)

	return render_template('authenticate.html',otp=encoded_OTP,main=userid,order=orderid)


@app.route('/enter_OTP', methods=['GET','POST'])
def enter_OTP():
	import datetime

	print("SSSSSSSSSSSS")
	userOTP = request.args.get('user_OTP')
	OTP=request.args.get('or_otp')
	userId = request.args.get('id')
	orderId =request.args.get('order_id')
	print(userOTP)
	print(OTP)
	encoded_userOTP = hashlib.sha512(userOTP.encode()).hexdigest()
	print(userId)
	print(orderId)
	if(OTP==encoded_userOTP) :
		print("YAYYYYYYYYYY")

		for x in Order.pending.find({},{"_id": 1, "User_Id": 1, "Status":1, "Delivery":1, "Price":1, "Time":1, "Order":1}):
			if(x['_id']==ObjectId(orderId)) :
				order = x["Order"]
				price = x["Price"]
				break

		d = datetime.datetime.now()

		entry = {
			'UserId' : userId,
			'Invoice' : orderId,
			'Date' : d.strftime("%x"),
			'Time' : d.strftime("%X"),
			'Price' : price,
			'Order' : order
		}

		entry = Order.order.insert_one(entry)

		myquery = { "_id": ObjectId(orderId)}
		newvalues = { "$set" : {"Status": 'Order Delivered' }}
		a = Order.pending.update_one(myquery, newvalues)

		user_mail = ''
		user_name = ''

		for x in db.info.find({},{"_id":1, "email":1, "name" :1}) :
			if(x['_id']==userId) :
				user_mail = x['email']
				user_name = x['name']

		try :
			SUBJECT = 'Invoice No: '+orderId+' Delivered'
			TEXT = 'Dear '+user_name+',\n\nYour Order of Invoice No. '+orderId+' is delivered.\nThank you for shopping with us.\n\nRegards-\nTeam Thella wala.'
			message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

			print(user_mail)

			mail = smtplib.SMTP('smtp.gmail.com',587)
			mail.ehlo()
			mail.starttls()
			mail.login(gmail_user, gmail_password)
			mail.sendmail(gmail_user,user_mail, message)
		except :
			print("Error sending the mail to "+user_mail)

		return redirect('previous_order?id='+userId)

	else :
		print("SHITTTTTTTTTT")

	return redirect('main_page.html?id='+userId)


@app.route('/change', methods = ['GET','POST'])
def change():
	print("asdasd")
	userId = request.args.get('id')
	product = request.args.get('product')
	value = request.args.get('value')
	print(userId)
	print(product)
	print(value)
	for x in db.cart.find({},{"_id": 0, "Customer_Id": 1, "Order":1}):
		if((x['Customer_Id'])==userId) :
			orders = x['Order']
			orders[product] = int(value)
			myquery = { "Customer_Id": userId }
			newvalues = { "$set" : {"Order": orders }}
			db.cart.update_one(myquery, newvalues)
			break

	return redirect('open_cart?id='+userId)


