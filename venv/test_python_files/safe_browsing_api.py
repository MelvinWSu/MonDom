import requests # For GET/POST HTTP requests in python
import json
import os

api_key = os.environ["GOOGLE_API_KEY"]

# TEST
# hard-code url value
url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
#myURL = "http://malware.testing.google.test/testing/malware/"

# ACTUAL
# user inputs a url value
x = input("Enter url: ")

if x.startswith('http://') or x.startswith('https://'):
    myURL = x
else:
    myURL = "http://" + x

print(myURL)

data = {'key': api_key}
payload = {"client": {'clientId': "", 'clientVersion': ""},
           "threatInfo": {'threatTypes': ["THREAT_TYPE_UNSPECIFIED", "MALWARE", "SOCIAL_ENGINEERING",
                                          "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                          'platformTypes': ["PLATFORM_TYPE_UNSPECIFIED", "WINDOWS", "LINUX", "ANDROID", "OSX", "IOS",
                                            "ANY_PLATFORM", "ALL_PLATFORMS", "CHROME"],
                          'threatEntryTypes': ["THREAT_ENTRY_TYPE_UNSPECIFIED", "URL", "EXECUTABLE"],
                          'threatEntries': [{'url': myURL}]
                          }
          }
r = requests.post(url, params=data, json=payload)
print(r)
print(r.json())

# api_key = os.environ["GOOGLE_API_KEY"]
# url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
# payload = {'client': {'clientId': "mycompany", 'clientVersion': "0.1"},
#         'threatInfo': {'threatTypes': ["SOCIAL_ENGINEERING", "MALWARE"],
#                        'platformTypes': ["ANY_PLATFORM"],
#                        'threatEntryTypes': ["URL"],
#                        'threatEntries': [{'url': "http://malware.testing.google.test/testing/malware/"}]}}
# params = {'key': api_key}
# r = requests.post(url, params=params, json=payload)
# # Print response
# print(r)
# print(r.json())