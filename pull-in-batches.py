import requests

url_id = "your-url-id"
token = "your-token"

url = "https://api.nightwatch.io/api/v1/urls/" + url_id + "/keywords"
params = {
    "access_token": token,
    "page": 1,
    "limit": 100
}

page = 1

results = []
while True:
    print(f'Pulling page {page}')
    params["page"] = page
    r = requests.get(url, params=params)
    json = r.json()
    results = results + json
    page = page + 1
    if (len(json) < 100):
        break

# print(results)

print(f'Pulled {len(results)} results')

# do anything with results that you wish
