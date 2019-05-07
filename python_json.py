#!/usr/bin/env python
import json
import urllib

url = "http://api.openweathermap.org/data/2.5/weather?id=3081368&APPID=5585c9a1202a2c2db9304f26e8f783ad"

json_url = urllib.urlopen(url)

data = json.loads(json_url.read())


print(data)
print("")
print(data["sys"])
