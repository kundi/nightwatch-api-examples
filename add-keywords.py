import requests
import csv
import sys

url_id = "304267"
token = "UKRYv0dRbQYBT7N5U0Ua9AdfXm8228BmD9eKtbPl9LY"

url = f"https://api.nightwatch.io/api/v1/urls/{url_id}/keywords/batch_create"
params = {"access_token": token}

data = {
    "keywords": "",
    "tags": [],
    "google_gl": "",
    "google_hl": "",
    "mobile": True,
    "desktop": False,
    "search_engine": "",
    "adwords_location_id": ""
}

read_file = "keywords.csv"
read_from = 1
read_max = 80000
per_batch = 1

keywords = []

settings = [
    ["keywords", 0],
    ["adwords_location_id", 7],
    ["tags", 1],
    ["google_gl", 2],
    ["google_hl", 3],
    ["mobile", 4],
    ["desktop", 5],
    ["search_engine", 6]
]

with open(read_file, newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f, delimiter=";")
    next(reader, None)  # Skip the header
    for row in reader:

        new_batch = False
        for setting in settings:
            if data[setting[0]] != row[setting[1]]:
                print(f"New setting for {setting[0]}: {data[setting[0]]} -> {row[setting[1]]}")
                new_batch = True

        if len(keywords) >= per_batch or (len(keywords) > 0 and new_batch):
            post = {
                "keywords": "\n".join(keywords),
                "tags": data["tags"],
                "google_gl": data["google_gl"],
                "google_hl": data["google_hl"],
                "mobile": data["mobile"],
                "desktop": data["desktop"],
                "search_engine": data["search_engine"],
                "adwords_location_id": data["adwords_location_id"]
            }

            print(post)

            response = requests.post(url, params=params, json=post)
            if response.status_code != 200:
                print(f"Request failed with status {response.status_code}: {response.text}")
            else:
                print("Success:", response.text)

            keywords = []

        keywords.append(row[0])  # Assuming keywords are in the first column, adjust if different
        data["adwords_location_id"] = row[7]
        data["tags"] = [row[1]]  # Assuming tags are in the second column, adjust if different
        data["google_gl"] = row[2]
        data["google_hl"] = row[3]
        data["mobile"] = row[4] == "TRUE"
        data["desktop"] = row[5] == "TRUE"
        data["search_engine"] = row[6]  # Assuming search engine is in the seventh column, adjust if different

# Ensure the last batch of keywords is posted
if len(keywords) > 0:
    post = {
        "keywords": "\n".join(keywords),
        "tags": data["tags"],
        "google_gl": data["google_gl"],
        "google_hl": data["google_hl"],
        "mobile": data["mobile"],
        "desktop": data["desktop"],
        "search_engine": data["search_engine"],
        "adwords_location_id": data["adwords_location_id"]
    }

    print(post)

    response = requests.post(url, params=params, json=post)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}: {response.text}")
    else:
        print("Success:", response.text)
