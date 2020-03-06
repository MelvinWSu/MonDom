import base64

print(base64.b64encode(bytes("https://waffles.com", "utf-8")))
print(base64.b64encode(bytes("https://www.waffles.com", "utf-8")))
print(base64.b64encode(bytes("www.waffles.com", "utf-8")))
print(base64.b64encode(bytes("waffles.com", "utf-8")))
print(base64.b64encode(bytes("192.168.0.1", "utf-8")))