from flask import Flask, render_template, request, redirect
import os
import pdb
import time
app = Flask(__name__)
regdata = {}
transfer = {}

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/register', methods = ['POST'])
def processRegistration():
    regdata["email"] = request.form['email']
    regdata["country_code"] = request.form['country_code']
    regdata["phone_number"] = request.form['phone_number']
    print("The phone number is '" + regdata["phone_number"] + "'")
    return redirect('/transaction')

@app.route('/processtransaction', methods = ['POST'])
def processTransaction():
    transfer["email"] = request.form['email2']
    transfer["acct"] = request.form['acct']
    transfer["amt"] = "$ " + request.form['amt']
    transfer["status"] = "Complete"
    print("The email address is '" + transfer["email"] + "'")
    print("The account number is '" + transfer["acct"] + "'")
    print("The US Dollar amount is '" + transfer["amt"] + "'")
    return redirect('/displaytransaction')

@app.route('/transaction')
def transaction():
    return render_template('transaction.html', regdata=regdata)

@app.route('/displaytransaction')
def displayTransaction():
    return render_template('displayTransaction.html', regdata=regdata, transfer=transfer)   

if __name__ == '__main__':
    app.run()