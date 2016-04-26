import requests
import platform
import pdb
from authy import __version__, AuthyFormatException
from urllib import quote

# import json
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json


class Resource(object):
    def __init__(self, api_uri, api_key):
        self.api_uri = api_uri
        self.api_key = api_key
        self.def_headers = self.__default_headers()

    def post(self, path, data = {}):
        return self.request("POST", path, data, {'Content-Type': 'application/json'})

    def get(self, path, data = {}):
        return self.request("GET", path, data)

    def put(self, path, data = {}):
        return self.request("PUT", path, data, {'Content-Type': 'application/json'})

    def delete(self, path, data = {}):
        return self.request("DELETE", path, data)

    def request(self, method, path, data = {}, headers = {}):
        url = self.api_uri + path
        params = {"api_key": self.api_key}
        headers = dict(self.def_headers.items() + headers.items())

        if method == "GET":
            params.update(data)
            return requests.request(method, url, headers=headers, params=params)
        else:
            return requests.request(method, url, headers=headers, params=params, data=json.dumps(data))

    def __default_headers(self):
        return {
            'User-Agent': "AuthyPython/{0} ({1}; Python {2})".format(
            __version__,
            platform.platform(True),
            platform.python_version()
        )}


class Instance(object):
    def __init__(self, resource, response):
        self.resource = resource
        self.response = response

        try:
            self.content = self.response.json()
        except ValueError:
            self.content = self.response.text

    def ok(self):
        return self.response.status_code == 200

    def errors(self):
        if self.ok():
            return {}

        errors = self.content

        if(not isinstance(errors, dict)):
            errors = {"error": errors} # convert to dict for consistency
        elif('errors' in errors):
            errors = errors['errors']

        return errors

    def __getitem__(self, key):
        return self.content[key]

class Sms(Instance):
    def ignored(self):
        try:
            self.content['ignored']
            return True
        except KeyError:
            return False

class User(Instance):
    def __init__(self, resource, response):
        super(User, self).__init__(resource, response)
        if(isinstance(self.content, dict) and 'user' in self.content):
            self.id = self.content['user']['id']
        else:
            self.id = None

class Onetouch(Instance):
    def __init__(self, resource, response):
        super(Onetouch, self).__init__(resource, response)
        if(isinstance(self.content, dict) and 'approval_request' in self.content):            
            self.uuid = self.content['approval_request']['uuid']
        else:
            self.uuid = None

class OnetouchStatus(Instance):
    def __init__(self, resource, response):
        super(OnetouchStatus, self).__init__(resource, response)
        if(isinstance(self.content, dict) and 'approval_request' in self.content):            
            self.status = self.content['approval_request']['status']
        else:
            self.status = None

class Users(Resource):
    def create(self, email, phone, country_code = 1):
        data = {
            "user": {
                "email": email,
                "cellphone": phone,
                "country_code": country_code
            }
        }

        resp = self.post("/protected/json/users/new", data)

        return User(self, resp)

    def request_sms(self, user_id, options = {}):
        resp = self.get("/protected/json/sms/"+quote(str(user_id)), options)

        return Sms(self, resp)

    def status(self, user_id):
        resp = self.get("/protected/json/users/{0}/status".format(user_id))

        return User(self, resp)

    def delete(self, user_id):
        resp = self.post("/protected/json/users/{0}/delete".format(user_id))

        return User(self, resp)

    def send_onetouch(self, user_id, options = {}):
        resp = self.post("/onetouch/json/users/{0}/approval_requests".format(user_id), options)

        return Onetouch(self, resp)

    def poll_onetouch(self, uuid):
        resp = self.get("/onetouch/json/approval_requests/{0}".format(uuid))

        return OnetouchStatus(self, resp)

class Token(Instance):
    def ok(self):
        if super(Token, self).ok():
            return '"token":"is valid"' in self.response.content
        return False

class Tokens(Resource):
    def verify(self, device_id, token, options = {}):
        self.__validate(token, device_id)
        if 'force' not in options:
            options['force'] = "true"
        resp = self.get("/protected/json/verify/"+quote(str(token))+"/"+quote(str(device_id)), options)
        return Token(self, resp)

    def __validate(self, token, device_id):
        self.__validate_digit(token, "Invalid Token. Only digits accepted.")
        self.__validate_digit(device_id, "Invalid Authy id. Only digits accepted.")
        length = len(token)
        if length < 6 or length > 10:
            raise AuthyFormatException("Invalid Token. Unexpected length.")

    def __validate_digit(self, var, message):
        if not isinstance(var, (int, long)) and not var.isdigit():
            raise AuthyFormatException(message)


class App(Instance):
    pass


class Apps(Resource):
    def fetch(self):
        resp = self.get("/protected/json/app/details")
        return App(self, resp)


class Stats(Instance):
    pass


class StatsResource(Resource):
    def fetch(self):
        resp = self.get("/protected/json/app/stats")
        return Stats(self, resp)

class Phone(Instance):
    pass

class Phones(Resource):
    def verification_start(self, phone_number, country_code, via = 'sms', locale = None):
        options = {
            'phone_number': phone_number,
            'country_code': country_code,
            'via': via
        }

        if locale:
            options['locale'] = locale

        resp = self.post("/protected/json/phones/verification/start", options)
        return Phone(self, resp)

    def verification_check(self, phone_number, country_code, verification_code):
        options = {
            'phone_number': phone_number,
            'country_code': country_code,
            'verification_code': verification_code
        }
        resp = self.get("/protected/json/phones/verification/check", options)
        return Phone(self, resp)

    def info(self, phone_number, country_code):
        options = {
            'phone_number': phone_number,
            'country_code': country_code
        }
        resp = self.get("/protected/json/phones/info", options)
        return Phone(self, resp)