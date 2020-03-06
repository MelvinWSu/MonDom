import requests  # For GET/POST HTTP requests in python
import json
import os
import base64
import datetime

api_key = os.environ["GOOGLE_API_KEY"]

import pyrebase

firebaseConfig = {
    "apiKey": "os.environ['FIREBASE_API_KEY']",
    "authDomain": "mondom-97740.firebaseapp.com",
    "databaseURL": "https://mondom-97740.firebaseio.com",
    "projectId": "mondom-97740",
    "storageBucket": "mondom-97740.appspot.com",
    "messagingSenderId": "877143682729",
    "appId": "1:877143682729:web:54f672e485632c73ad43b8",
    "measurementId": "G-6S2J42P9KP"
};

firebase = pyrebase.initialize_app(firebaseConfig)

# TEST
# hard-code url value
# myURL = "malware.testing.google.test/testing/malware/"
# myURL = "malware.wicar.org"

# ACTUAL
# user inputs a url value
x = input("Enter url: ")

if x.startswith('http://') or x.startswith('https://'):
    myURL = x
else:
    myURL = "http://" + x

# Print url input
# print(myURL)

# Needed to use Google Safe Browsing API
url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

# Format for data
data = {'key': api_key}

# Body of HTTP response
payload = {"client": {'clientId': "", 'clientVersion': ""},
           "threatInfo": {'threatTypes': ["THREAT_TYPE_UNSPECIFIED", "MALWARE", "SOCIAL_ENGINEERING",
                                          "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                          'platformTypes': ["PLATFORM_TYPE_UNSPECIFIED", "WINDOWS", "LINUX", "ANDROID", "OSX", "IOS",
                                            "ANY_PLATFORM", "ALL_PLATFORMS", "CHROME"],
                          'threatEntryTypes': ["THREAT_ENTRY_TYPE_UNSPECIFIED", "URL", "EXECUTABLE"],
                          'threatEntries': [{'url': myURL}]
                          }
           }

print(myURL)

# POST request
r = requests.post(url, params=data, json=payload)

# Print response
print(r)
print(r.json())


info = {
    "url":myURL,
    "last_update":datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    "IP_address":"000.000.000.000"
}
firebase = firebase.database()
firebase.child("database").child(base64.b64encode(bytes(myURL, "utf-8"))).child("safebrowsing").set(r.json())
firebase.child("database").child(base64.b64encode(bytes(myURL, "utf-8"))).update(info)
# returns type of threat and platform it affects
