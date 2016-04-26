<a href="http://twilio.com/signal">![](https://s3.amazonaws.com/baugues/signal-logo.png)</a>

Join us in San Francisco May 24-25th to [learn directly from the developers who build Authy](https://www.twilio.com/signal/schedule/2crLXWsVZaA2WIkaCUyYOc/aut).

# Two-Factor Authentication with Authy OneTouch REST APIs and Python

Here you will learn how to use the Authy OneTouch REST APIs to perform a user registration, send an approval request, poll the status of the request, display transaction information, etc.

[Learn more about this code in our interactive code walkthrough](https://www.twilio.com/docs/howto/walkthrough/two-factor-authentication/python/flask).

## Quickstart

### Create a Twilio account

Create a free [Twilio account](https://www.twilio.com/user/account/authy/getting-started) and access the Authy dashboard.

### Setup the environment

This example assumes you already have [Python](https://www.python.org/) already installed on your machine.

This project is built using the [Flask](http://flask.pocoo.org/) web framework.

1. First clone this repository and `cd` into it.

   ```bash
   $ git clone https://github.com/dkillmer/authy-workshop-python.git
   $ cd authy-workshop-python
   ```

1. Install the dependencies.

   ```bash
   $ ???
   ```

1. Export the environment variable (AUTHY\_API\_KEY).

   You can find your AUTHY API KEY for Production at https://dashboard.authy.com/.

   ```bash
   $ export AUTHY_API_KEY=Your Authy API Key
   ```
   If you are using a non-UNIX operating system, make sure that the AUTHY_API_KEY is loaded into your environment.

1. Run the server.

   ```bash
   $ python authyonetouch.py
   ```

1. Open up your web browser and navigate to [http://localhost:5000](http://localhost:5000)

That's it!

### Workshop Objectives

The objectives of this workshop are for you to successfully register a new Authy user in your application, send an Authy OneTouch transaction approval request to your Authy app, approve or deny the ficticious money transfer transaction and display the completed transaction.

####Register the User
Before you can secure a user's login or enforce a second factor you need to create an Authy user. Authy requires you send an email, cellphone and country code for each Authy user. In response you get an Authy ID which you must then store with your user's profile in your own application.

The API Endpoint documentation for enabling two-factor authentication for a user is located [here](http://docs.authy.com/totp.html#enabling-two-factor-authentication-for-a-user)

In this sample, we are using a modified version of the [Authy API library for python](https://github.com/authy/authy-python), which has been included in this github repository. Do not download the version from github for this workshop.  Using the included Authy library, here is an example API call for registering the user, which returns a unique Authy ID:

```
authy_api.users.create('user@email.com','555-555-5555','1')
    # returns {user: {id: 1337}} where 1337 = Authy ID assigned to the user
```

####Creating the Approval Request
This is the main endpoint. This will create a new approval request for the given Authy ID and send it to the end user along with a push notification to the Authy smartphone application.

The API Endpoint documentation for Creating the Approval Request is located [here](http://docs.authy.com/onetouch.html#create-approvalrequest)

Here is an example API call for creating an approval request, which will return a unique transaction identifier called uuid:

```
message = {    "message":"Transfer Money to" + transfer["email"],    "details": {        "From":regdata["email"],        "To":transfer["email"],        "Account Number":transfer["acct"],        "US Dollar Amount":transfer["amt"]        },    "seconds_to_expire":"600"        }
authy_api.users.send_onetouch(regdata["authyid"], message)

```						 

####Checking for Approval Request Status

The final step is to provide the status of the approval request to the user (typically approved or denied).

The API Endpoint documentation for Checking for Approval Request Status is located [here](http://docs.authy.com/onetouch.html#check-approvalrequest-status)

Here is an example API call for checking for Approval Request Status, and one implementation of a polling loop.  Once the status changes to approved, denied or expired, the loop will exit:

```
    while True:        onetouchStatus = authy_api.users.poll_onetouch(onetouch.uuid)        print "Authy Onetouch Approval Status: %s " % onetouchStatus.status        if onetouchStatus.status != "pending" :            break        time.sleep(1)    transfer["status"] = onetouchStatus.status

```

## Running our complete solution
If you want to see a complete solution running, navigate to the solution folder under your project and run the server from there.
   
   ```bash
   $ cd solution
   $ python authyonetouch.py
   ```

## Meta

* No warranty expressed or implied. Software is as is.
* [Apache License](https://opensource.org/licenses/Apache-2.0)