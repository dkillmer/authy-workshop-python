from authy.api import AuthyApiClient
from flask import Flask, render_template, request, redirect
import os
import pdb
import time
app = Flask(__name__)
regdata = {}
transfer = {}
authy_api_key = os.environ['AUTHY_API_KEY']
authy_api = AuthyApiClient(authy_api_key)


@app.route('/')
def register():
    return render_template('register.html')

@app.route('/register', methods = ['POST'])
def processRegistration():
    regdata["email"] = request.form['email']
    regdata["country_code"] = request.form['country_code']
    regdata["phone_number"] = request.form['phone_number']
    print("The phone number is '" + regdata["phone_number"] + "'")
    user = authy_api.users.create(regdata["email"],regdata["phone_number"],regdata["country_code"])
    if user.ok():
        print "Authy ID = %s " % user.id
        regdata["authyid"]=user.id
    else:
        print user.errors()	
    return redirect('/transaction')

@app.route('/processtransaction', methods = ['POST'])
def processTransaction():
    transfer["email"] = request.form['email2']
    transfer["acct"] = request.form['acct']
    transfer["amt"] = "$ " + request.form['amt']
    print("The email address is '" + transfer["email"] + "'")
    print("The account number is '" + transfer["acct"] + "'")
    print("The US Dollar amount is '" + transfer["amt"] + "'")
    print regdata["authyid"]
    message = {
    "message":"Transfer Money to " + transfer["email"],
    "details": {
        "From":regdata["email"],
        "To":transfer["email"],
        "Account Number":transfer["acct"],
        "US Dollar Amount":transfer["amt"]
        },
    "seconds_to_expire":"600"    
    }
    print message   
    onetouch = authy_api.users.send_onetouch(regdata["authyid"], message)
    print onetouch.uuid
    while True:
        onetouchStatus = authy_api.users.poll_onetouch(onetouch.uuid)
        print "Authy Onetouch Approval Status: %s " % onetouchStatus.status
        if onetouchStatus.status != "pending" :
            break
        time.sleep(1)
    transfer["status"] = onetouchStatus.status
    transfer["transactionID"] = onetouch.uuid 
    return redirect('/displaytransaction')

@app.route('/transaction')
def transaction():
    return render_template('transaction.html', regdata=regdata)

@app.route('/displaytransaction')
def displayTransaction():
    return render_template('displayTransaction.html', regdata=regdata, transfer=transfer)   

if __name__ == '__main__':
    app.run()