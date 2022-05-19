import requests
import csv

# set url id
url_id = ""

# set API token
token = ""

url = "https://api.nightwatch.io/api/v1/urls/" + url_id + "/keywords"
params = {
    "access_token": token,
    "page": 1,
    "limit": 100,
#    "dynamic_view_id": 11111
}

page = 1

f = open('report.csv', 'w')
writer = csv.writer(f)

results = []
while True:
    print(f'Pulling page {page}')
    params["page"] = page
    r = requests.get(url, params=params)
    json = r.json()
    # results = results + json
    for r in json:
        tags = []
        if r["tags"]:
            for t in r["tags"]:
                print(t["id"])
                tags.append(t["id"])

        position = r["position"] or 0
        row = [ r["query"], position, r["local_search"], ",".join(tags) ]
        print(row)
        writer.writerow(row)
    
    page = page + 1
    if (len(json) < 100):
        break

f.close()

print(f'Pulled {len(results)} results')

