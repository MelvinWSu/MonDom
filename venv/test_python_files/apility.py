import apilityio
from datetime import datetime
import requests
import validators

client = apilityio.Client(api_key='028d21b2-bad9-4db6-8564-0f60159ee65b')

#TEST IP
# ip = '127.0.53.53'
# ip = '0.21.6.27'
# ip = '151.101.0.81'
# ip = '173.0.51.121'

#TEST DOMAIN
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

print("IP Result:")
if response.status_code == 404:
    print("Congratulations! The IP address has not been found in any blacklist.")

if response.status_code == 200:
    print("Ooops! The IP address has been found in one or more blacklist")
    blacklists = response.blacklists
    print('+- Blacklists: %s' % blacklists)

geo = client.GetWhoisIP(IP)
print(geo.json)