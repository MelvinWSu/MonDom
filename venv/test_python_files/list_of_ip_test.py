import pandas as pd
import apilityio

export = pd.read_csv('list_of_ip.csv', header=None)
ip_list = export.values.T[0].tolist()

#print(ip_list)

client = apilityio.Client(api_key='028d21b2-bad9-4db6-8564-0f60159ee65b')

for item in ip_list:
    response = client.CheckIP(item)

    if response.status_code == 404:
        print("Good IP")

    if response.status_code == 200:
        print("Bad IP")