import os, re
from model import *
from flask import Flask, session, request, flash, url_for, redirect, render_template, abort, jsonify
# import flask_login
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from functools import wraps


app = Flask(__name__)

def login_required(userinput):
	@wraps(userinput)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return userinput(*args, **kwargs)
		else:
			flash("You need to login first.")
			return redirect('/login')
	return wrap

# =====================================================================================================
# Routes ==============================================================================================
# =====================================================================================================

@app.route("/", methods=['POST','GET'])
def index():
	email = ''
	if session.get('logged_in'):
		email = session.get('email')
		print("session logged in = true")
		return redirect("/home")
	else:
		print("session logged in = false")
		return redirect("/login")

@app.route("/dashboard", methods=['POST','GET'])
@login_required
def dashboard():
	title = "Main Dashboard"
	return render_template("main.html",
		title = title)

@app.route("/login", methods=['POST','GET'])
def login():
	error_msg = ""
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		user = User.query.filter_by(email=email).first()
		print("email:", email)
		print("user:", user)
		if user:
			print("user.check_password(password):", user.check_password(password))
			if user.check_password(password):
				session['logged_in'] = True
				session['firstname'] = user.firstname
				session['id'] = user.id
				print("/Login: successfully logged in")
				return redirect('/home')
		error_msg = "Incorrect email/password. Please try again."
	return render_template("login.html", error_msg = error_msg)


@app.route("/register", methods = ['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html')
	user = User(request.form['email'], request.form['password'], request.form['firstname'], request.form['lastname'])
	db.session.add(user)
	db.session.commit()
	print("User successfully added.")
	return redirect('/login')

@app.route("/logout")
@login_required
def logout():
	session.clear()
	print("User logged out.")
	return redirect('/login')

@app.route("/home", methods=['GET','POST'])
@login_required
def home():
	return render_template('home.html')


@app.route("/org_dashboard", methods=['GET','POST'])
@login_required
def org_dashboard():
	title = "Original Dashboard"
	return render_template("org_dashboard.html",
		title = title)

@app.route("/proforma", methods=['GET','POST'])
@login_required
def proforma():
	title = "Pro Forma"
	return render_template("proforma.html",
		title=title)

@app.route('/returns_summary', methods=['GET','POST'])
@login_required
def return_sum():
	title = "Returns Summary"
	return render_template('returns_summary.html',
		title=title)

@app.route('/inputform')
@login_required
def inputForm():
	title="Input Form"
	return render_template('input_form.html',
		title = title)

@app.route('/savedata',methods = ["POST"])
@login_required
def save_data():
	print('='*50+" start save")
	market_counter = 1
	rental_rate_counter = 1
	# rental rate lists
	proj_rents_list = []
	total_units_list = []
	avg_sf_per_unit_list = []
	rent_per_unit_list = []
	# market rental lists
	revenue_list = []
	expenses_list = []
	vacancy_list = []
	concession_list = []
	credit_loss_list = []
	# static inputs
	save = RealEstateModel(datetime.utcnow(),
				request.form['save_name'],
				request.form['Analysis_Start_Date'],
				request.form['Property_Name'],
				request.form['Property_Address'],
				request.form['Property_Type'],
				request.form['Purchase_Price'],
				request.form['Closing_Costs_Percentage'],
				request.form['Sale_Year'],
				request.form['Terminal_Cap_Rate'],
				request.form['Sales_Costs'],
				request.form['Leverage'],
				request.form['Interest_Rate_on_Mortgage'],
				request.form['Loan_Term'],
				request.form['Loan_Amortization'],
				'5',# request.form['UL_Discount_Rate'],
				'8',# request.form['L_Discount_Rate'],
				request.form['Other_Income_Total'],
				request.form['Less_Vacancy'],
				request.form['Less_Concessions'],
				request.form['Less_Credit_Loss'],
				request.form['Real_Estate_Taxes_Total'],
				request.form['Insurance_Total'],
				request.form['Utilities_Total'],
				request.form['Payroll_Total'],
				request.form['Repairs_and_Maintenance_Total'],
				request.form['Contract_Services_Total'],
				request.form['Turnover_Total'],
				request.form['Sales_and_Marketing_Total'],
				request.form['Administrative_Total'],
				request.form['Management_Percentage'],
				request.form['Replacement_Reserves_Percentage'],
				session['id'])

	db.session.add(save)
	# db.session.commit()



	while True:
		if not request.form.get('total_units'+str(rental_rate_counter)):
			break
		proj_rents_list.append(request.form['proj_rents'+str(rental_rate_counter)])
		total_units_list.append(request.form['total_units'+str(rental_rate_counter)])
		avg_sf_per_unit_list.append(request.form['avg_sf_per_unit'+str(rental_rate_counter)])
		rent_per_unit_list.append(request.form['rent_per_unit'+str(rental_rate_counter)])
		rental_rate_counter += 1

	while True:
		if not request.form.get('mkt_rent_revenue'+str(market_counter)):
			print('break')
			break
		revenue_list.append(request.form['mkt_rent_revenue'+str(market_counter)])
		expenses_list.append(request.form['mkt_rent_expenses'+str(market_counter)])
		vacancy_list.append(request.form['mkt_rent_vacancy'+str(market_counter)])
		concession_list.append(request.form['mkt_rent_concessions'+str(market_counter)])
		credit_loss_list.append(request.form['mkt_rent_credit_loss'+str(market_counter)])
		market_counter += 1
		print(market_counter)


	# print('proj_rents_list: ',proj_rents_list)
	# print('total_units_list: ',total_units_list)
	# print('avg_sf_per_unit_list: ',avg_sf_per_unit_list)
	# print('rent_per_unit_list: ',rent_per_unit_list)


	print('revenue_list: ',revenue_list)
	print('expenses_list: ',expenses_list)
	print('vacancy_list: ',vacancy_list)
	print('concession_list: ',concession_list)
	print('credit_loss_list: ',credit_loss_list)

	return jsonify(success = 'success')




if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	# app.run(port=3000,debug=True)			#Runs on local host :3000
	app.run(host='0.0.0.0', debug=True)		#Runs using computer's IP address
