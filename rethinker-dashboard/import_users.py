from __future__ import print_function, unicode_literals
from pprint import pprint
from urllib.parse import urlencode
import csv
import time
import asyncio
import os
import requests
import rethinkdb as r


REQUESTS = []
LOC_CACHE = {}

#    https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY

def load_cache():
    if os.path.exists(".cache"):
        with open(".cache", "r") as o:
            for line in o.readlines():
                line = line.strip()
                pprint(line)
                key, value = line.split("|")
                lng, lat = value.split(",")
                LOC_CACHE[key] = dict(
                    lng = lng,
                    lat = lat
                )

#r.table("users").insert(users.values()).run(conn)
if __name__ == "__main__":

    load_cache()

    path = "/Users/dalanmiller/Dropbox (RethinkDB)/Case Studies/contributors-stargazers-lists"

    users = {}

    for file_name in os.listdir(path):
        if '.csv' in file_name:
            with open(os.path.join(path,file_name), 'r') as o:
                reader = csv.DictReader(o)
                for user in reader:
                    users[user['id']] = user

    loop = asyncio.get_event_loop()
    tasks = []

    for v in [x for x in users.values()][:200]:
        if v['location'] not in ("", None, "None") and v['location'] not in LOC_CACHE:
            d = {
                "address": v['location'],
                "key": "AIzaSyDmA9x7KluWqBLkm7ktegBBe6tJGTg3QiI"
            }

            url = "https://maps.googleapis.com/maps/api/geocode/json?{}".format(
                urlencode(d)
            )
            future = loop.run_in_executor(None, requests.get, url)
            print("Adding to tasks! - {}".format(url))
            tasks.append(future)
            v['future'] = future

    begin = time.time()
    print("Waiting for loop to end - {}".format(begin))
    loop.run_until_complete(asyncio.wait(tasks))
    end = time.time() - begin
    print("Finished - {}".format(end))

    loop.close()

    for user in users.values():
        if v['location'] not in LOC_CACHE and 'future' in user:
            resp_json = user['future'].result().json()
            # if 'results' in resp_json and len(resp_json['results']):
            #     pprint(resp_json['results'][0])
            try:
                geo = resp_json['results'][0]['geometry']['location']
                user['geo_point'] = r.point(geo['lng'], geo['lat'])

                if user['location'] not in LOC_CACHE:
                    LOC_CACHE[user['location']] = dict(
                        lng = geo['lng'],
                        lat = geo['lat']
                    )

            except Exception as e:
                print("Something fucked up")
                print(e)

        elif user['location'] in LOC_CACHE:
            geo = LOC_CACHE[user['location']]
            user['geo_point'] = r.point(geo['lng'], geo['lat'])

    with open(".cache", "w") as o:
        for k,v in LOC_CACHE.items():
            if k != None:
                o.write("{}|{},{}\n".format(k, v['lng'], v['lat']))

    conn = r.connect("localhost", 28015, db="users_dashboard")

    geo_located_users = [x for x in users.values() if 'geo_point' in x]
    print(
        r.table(
            "users"
        ).insert(
            geo_located_users,
            conflict="replace"
        ).run(conn)
    )
