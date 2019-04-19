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


app = Flask(__name__)
client = MongoClient(port=27017)
db=client.user


@app.route("/")
def hello():
    return "Hello World!"


"""
@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
    """

@app.route('/login.html', methods=['GET','POST'])
def login():
	print("index returned")
	return render_template('login.html')

@app.route('/forgotPassword.html', methods=['GET','POST'])
def forgot_pass():
	return render_template('forgotPassword.html')

@app.route('/cart.html', methods=['GET','POST'])
def view_cart():
	print("index returned")
	return render_template('cart.html')

@app.route('/main_page.html', methods=['GET','POST'])
def main():
	print("index returned")
	return render_template('main_page.html')

@app.route('/handle_data', methods=['POST'])
def handle_data():
	print("Here")
	userEmail = request.form['email']
	userPassword = request.form['pass']
	encoded_password = hashlib.sha512(userPassword.encode()).hexdigest()
	print(userEmail)
	print(userPassword)

	ret_query = db.info.find_one({'email': userEmail})
	try :
		if ret_query['password'] == encoded_password :
			return "Log in"
		else :
			#return render_template('index_wrong_pass.html')
			return jsonify(result="Wrong Password is it.")
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
			print('Added')
		else :
			print('Error')

	return render_template('signup.html')

	#ret_query = db.info.find_one({'email': userEmail})
	#try :
	#	if ret_query['password'] == userPassword :
	#		return "Log in"
	#	else :
	#		return render_template('index_wrong_pass.html')
	#except TypeError:
	#	return "User not recognized \n Try to Sign Up."
	#return "Fuck Off"

"""
@app.route('/forgotPassword.html', methods=['GET','POST'])
def forgotPassword():
	return render_template('forgotPassword.html')
	"""

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

@app.route('/add_to_cart', methods=['GET','POST'])
def add_cart():
	return 1

@app.route('/cart.html', methods=['GET','POST'])
def cartup():
	return render_template('cart.html')

@app.route('/add_tomato', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	return render_template('main_page.html')
@app.route('/add_carrot', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	return render_template('main_page.html')

@app.route('/add_potato', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	return render_template('main_page.html')
@app.route('/add_cucumber', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	if(counter==0) :
		orders = {"cucumber":1}
		entry = {
		'Customer_Id' : userId,
		'Order' : orders,
		}
		db.cart.insert_one(entry)
	return render_template('main_page.html')

@app.route('/add_broccoli', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	return render_template('main_page.html')
	
@app.route('/add_peas', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	return render_template('main_page.html')

@app.route('/add_cabbage', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	return render_template('main_page.html')

@app.route('/add_onion', methods=['POST'])
def add_tomato():
	counter=0
	userId = '5cacb24a5f627d34c743feb7'
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
	return render_template('main_page.html')














@app.route('/blog.html', methods=['GET','POST'])
def blogup():
	return render_template('blog.html')

