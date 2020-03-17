import pandas as pd
import apilityio

export = pd.read_csv('list_of_ip.csv', header=None)
ip_list = export.values.T[0].tolist()

#print(ip_list)

client = apilityio.Client(api_key='028d21b2-bad9-4db6-8564-0f60159ee65b')


# This is to get IP and their corresponding blacklists (if any) using CheckBatchIP()
# It is faster than iterating through each ip in the list and getting their individual HTTP responses
response = client.CheckBatchIP(ip_list)
for item in response.json.get("response"):
    print(item.get("ip"))
    if not item.get("blacklists"):
        print("Not Found")
    else:
        print(item.get("blacklists"))

# This gets an HTTP response back from each individual ip using CheckIP()
# It is slower than getting them all from a batch request using CheckBatchIP()
#print(response.json.get("response"))
#
# for item in ip_list:
#     response = client.CheckIP(item)
#
#     if response.status_code == 404:
#         print("Good IP")
#
#     if response.status_code == 200:
#         print("Bad IP")