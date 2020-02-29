import requests
import json

api_key='AIzaSyCqAMAZW8g15kvk7fGIK3vHpZjk42MQz5c'
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