import json
import os

import requests

class Weather:
    def get_data(self,city):

        url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
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
            info['start_time'] = weather_elements[0]["time"][0]["startTime"]
            info['end_time'] = weather_elements[0]["time"][0]["endTime"]
            info['weather_state'] = weather_elements[0]["time"][0]["parameter"]["parameterName"]
            info['rain_prob'] = weather_elements[1]["time"][0]["parameter"]["parameterName"]
            info['min_tem'] = weather_elements[2]["time"][0]["parameter"]["parameterName"]
            info['comfort'] = weather_elements[3]["time"][0]["parameter"]["parameterName"]
            info['max_tem']= weather_elements[4]["time"][0]["parameter"]["parameterName"]

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