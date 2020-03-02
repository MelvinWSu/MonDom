import requests # For GET/POST HTTP requests in python
import json
import os

api_key = os.environ["GOOGLE_API_KEY"]

# TEST
# hard-code url value
# myURL = "http://malware.testing.google.test/testing/malware/"
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

# POST request
r = requests.post(url, params=data, json=payload)

# Print response
print(r)
print(r.json())
# returns type of threat and platform it affects