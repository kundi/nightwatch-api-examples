import requests
import csv
import sys
import time
​
url_id = ""
token = ""
​
url = "https://api.nightwatch.io/api/v1/urls/" + url_id + "/keywords/batch_create"
params = {
    "access_token": token
}
​
data = {
    "keywords": "",
    "tags": [ ],
    "google_gl": "in",
    "google_hl": "en",
    "mobile": True,
    "desktop": False,
    "search_engine": "google",
    "adwords_location_id": ""
}
​
read_file = "keywords.csv"
​
read_from = 1
read_max = 80000
​
l = 0
p = 0
​
per_batch = 1
​
location = ""
keywords = []
​
settings = [ ["adwords_location_id", 1], ["tags", 2] ]
with open(read_file, newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        l=l+1
        # print(row[1])
        # set current location
​
        if l >= read_from: 
            p=p+1
​
            if (p >= read_max):
                print(f"reached {read_max}")
                sys.exit()
​
            # adding batch
            new_batch = False
            for setting in settings:
                # check if we have a different setting than previously
                if data[setting[0]] != row[setting[1]]:
                    print(f"new setting for {setting[0]}: {data[setting[0]]} - {row[setting[1]]}")
                    new_batch = True
​
            if ( len(keywords) >=  per_batch or ( len(keywords) > 0 and new_batch ) ):
                post = {}
                post = data
                post["adwords_location_id"] = data["adwords_location_id"]
                post["tags"] = [ data["tags"] ]
                post["keywords"] = "\n".join(keywords)
                print(post)
​
                r = requests.post(url, params=params, data=post)
                print(r)
            #   time.sleep(5)
                keywords = []
            
            keywords.append(row[0])
            # data["adwords_location_id"] = locations.get(row[1])
            data["adwords_location_id"] = row[1]
            data["tags"] = row[2]
​
        # print(row)
