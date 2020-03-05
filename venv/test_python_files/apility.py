import apilityio
import requests
import validators

client = apilityio.Client(api_key='028d21b2-bad9-4db6-8564-0f60159ee65b')

#TEST
# ip = '127.0.53.53'
# ip = '0.21.6.27'
ip = '151.101.0.81'
response = client.CheckIP(ip)

if response.status_code == 404:
    print("Congratulations! The IP address has not been found in any blacklist.")

if response.status_code == 200:
    print("Ooops! The IP address has been found in one or more blacklist")
    blacklists = response.blacklists
    print('+- Blacklists: %s' % blacklists)

