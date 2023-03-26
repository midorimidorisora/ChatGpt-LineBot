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
            # print(response.encoding)
            # response.encoding='utf-8-sig'
            data = json.loads(response.text)
            info={}
            info['location'] = data["records"]["location"][0]["locationName"].encode('utf-8')

            weather_elements = data["records"]["location"][0]["weatherElement"]
            info['TEMP'] = weather_elements[3]["elementValue"]
            info['HUMD'] = weather_elements[4]["elementValue"]
            info['PRES'] = weather_elements[5]["elementValue"]
            info['Weather'] = weather_elements[20]["elementValue"].encode('utf-8')
            info['ELEV'] = weather_elements[0]["elementValue"]
            info['WDIR'] = weather_elements[1]["elementValue"]
            info['WDSD']= weather_elements[2]["elementValue"]

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