import requests
import csv
import codecs


url_id = "317483"
token = "c-novqTfkUzrNZ63b8e5o0jfm2Pw27T4rXI6MGYD65I"

url = "https://api.nightwatch.io/api/v1/urls/" + url_id + "/keywords"
competitor_url = "https://api.nightwatch.io/api/v1/urls/" + url_id + "/competitors"

params = {
    "access_token": token,
    "page": 1,
    "limit": 100,
}

page = 1

f = codecs.open('report.csv', 'w', 'utf-8')
writer = csv.writer(f)

results = []

req_comp = requests.get(competitor_url, params=params, headers={"Content-Type": "application/json"})
competitors_json = req_comp.json()

def handle_competitors(competitor_results):
    ids = list(competitor_results.keys())

    cdata = []

    for c in competitors_json:
        found = False
        for cres_id in ids:
            cid = str(c.get("id"))
            if cres_id == cid:
                cdata.append({"competitor": c, "data": competitor_results.get(cid)})
                found = True

        if not found:
            cdata.append(None)

    return cdata


def competitor_header():
    ctitles = []
    for c in competitors_json:
        ctitles.append("Competitor " + c.get("display_name", ""))

    return ctitles


def competitor_table(cdata):
    clist = []

    for c in cdata:
        data = c.get("data")
        clist.append(data.get("rank", ""))
    return clist


def enc(str):
    if str is None:
        return ''
    return str


def try_print(row):
    try:
        print(row)
    except:
        return None

writer.writerow(["Query", "Position", "Local search", "Tags", "Url", *competitor_header()])

while True:
    try_print(f'Pulling page {page}')
    params["page"] = page
    r = requests.get(url, params=params)
    json = r.json()

    for r in json:
        tags = []
        if r["tags"]:
            for t in r["tags"]:
                print(t["id"])
                tags.append(t["id"])

        position = r["position"] or 0
        competitors = r.get("competitor_results", [])  # Get "competitor_results" if exists, else use an empty list

        if competitors:  # Check if "competitor_results" is not empty or None
            competitor_list = handle_competitors(competitors)
        else:
            competitor_list = []  # Set an empty list if "competitor_results" is not available

        row = [
            enc(r["query"]),
            position,
            r["local_search"],
            enc("|".join(tags)),
            enc(r["url"]),
            *competitor_table(competitor_list),
        ]
        try_print(row)
        writer.writerow(row)
    
    page = page + 1
    if (len(json) < 100):
        break

f.close()

try_print(f'Pulled {len(results)} results')
