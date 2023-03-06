import json
import os

import requests

class Weather:
    def get_data(city):

        url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001"
        params = {
            "Authorization": "CWB-513C160C-774E-4A37-B382-385E3C37B154",
            "locationName": city,
        }

        response = requests.get(url, params=params)
        print(response.status_code)

        if response.status_code == 200:
            # print(response.text)
            data = json.loads(response.text)
            info={}
            info['location'] = data["records"]["location"][0]["locationName"]

            weather_elements = data["records"]["location"][0]["weatherElement"]
            info['TEMP'] = weather_elements[3]
            info['HUMD'] = weather_elements[4]
            info['PRES'] = weather_elements[5]
            info['Weather'] = weather_elements[20]
            info['ELEV'] = weather_elements[0]
            info['WDIR'] = weather_elements[1]
            info['WDSD']= weather_elements[2]

            # print(location)
            # print(start_time)
            # print(end_time)
            # print(weather_state)
            # print(rain_prob)
            # print(min_tem)
            # print(comfort)
            # print(max_tem)
            return json.dumps(info)
        else:
            print("Can't get data!")