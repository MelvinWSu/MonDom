import apilityio
from datetime import datetime
import pyrebase
import requests
import validators
import base64

import json
import os
import datetime

import os.path
import csv
import time
import urllib3
import pyrebase

#configs
api_key = os.environ["GOOGLE_API_KEY"]

firebaseConfig = {
    "apiKey": "os.environ['FIREBASE_API_KEY']",
    "authDomain": "mondom-97740.firebaseapp.com",
    "databaseURL": "https://mondom-97740.firebaseio.com",
    "projectId": "mondom-97740",
    "storageBucket": "mondom-97740.appspot.com",
    "messagingSenderId": "877143682729",
    "appId": "1:877143682729:web:54f672e485632c73ad43b8",
    "measurementId": "G-6S2J42P9KP"
}

firebase = pyrebase.initialize_app(firebaseConfig)

client = apilityio.Client(api_key='028d21b2-bad9-4db6-8564-0f60159ee65b')

#---------------safebrowsing
def safebrowsing():

    x = input("Enter url: ")

    if x.startswith('http://') or x.startswith('https://'):
        myURL = x
    else:
        myURL = "http://" + x

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

    info = {
        "url":myURL,
        "last_update":datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "IP_address":"000.000.000.000"
    }
    firebase = firebase.database()
    firebase.child("database").child(base64.b64encode(bytes(myURL, "utf-8"))).child("safebrowsing").set(r.json())
    firebase.child("database").child(base64.b64encode(bytes(myURL, "utf-8"))).update(info)
    return r.json
# returns type of threat and platform it affects

#------------apility
def apilityRetrieve():

    domain = 'malware.wicar.org'

    #START
    res = client.CheckDomain(domain)
    transaction = client.GetHistoryDomain(domain)
    IP = res.json.get("response").get("ip").get("address")
    response = client.CheckIP(IP)

    print("Domain Result: ")
    if res.status_code == 404:
        print("Congratulations! The domain has not been found in any blacklist.")

    if res.status_code == 200:
        print("Ooops! The domain has been found in one or more blacklist")

    print("Transactions:")
    for items in transaction.json.get("changes_domain"):
        timestamp = items.get("timestamp")
        dt_obj = datetime.fromtimestamp(timestamp//1000)
        print(str(dt_obj) + " " + items.get("command") + " " + items.get("blacklists") + " " + items.get("blacklist_change"))

    b64encoded = base64.b64encode(bytes("http://" + domain, "utf-8"))
    website_results = firebase.database().child("database").child(b64encoded).child("apility")
    website_results.push(transaction.json)

    print("IP Result:")
    if response.status_code == 404:
        print("Congratulations! The IP address has not been found in any blacklist.")

    if response.status_code == 200:
        print("Ooops! The IP address has been found in one or more blacklist")
        blacklists = response.blacklists
        print('+- Blacklists: %s' % blacklists)

    geo = client.GetWhoisIP(IP)
    print(geo.json) #change to append

#-------------------virustotal
