import requests
import os

API_KEY = os.environ["WEREAD_API_KEY"]

url = "https://i.weread.qq.com/api/agent/gateway"

data = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "api_name": "/readdata/detail",
        "mode": "overall",
        "baseTime": 0,
        "skill_version": "1.0.4",
    },
).json()

weread_data = dict()

weread_data['readDays'] = data['readDays']
weread_data['preferCategory'] = data['preferCategory']
weread_data['readStat'] = data['readStat']
weread_data['totalReadTime'] = data['totalReadTime']
weread_data['totalReadTime_str'] = f"{round(data['totalReadTime'] / 3600)}小时"

# %%
import json

with open("weread.json", "w") as f:
    json.dump(weread_data, f, ensure_ascii=False, indent=4)
