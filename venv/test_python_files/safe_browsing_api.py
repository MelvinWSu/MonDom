import requests
import json
import os

api_key = os.environ["GOOGLE_API_KEY"]
url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
payload = {'client': {'clientId': "mycompany", 'clientVersion': "0.1"},
        'threatInfo': {'threatTypes': ["SOCIAL_ENGINEERING", "MALWARE"],
                       'platformTypes': ["ANY_PLATFORM"],
                       'threatEntryTypes': ["URL"],
                       'threatEntries': [{'url': "http://malware.testing.google.test/testing/malware/"}]}}
params = {'key': api_key}
r = requests.post(url, params=params, json=payload)
# Print response
print(r)
print(r.json())