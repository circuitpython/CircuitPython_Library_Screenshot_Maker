# SPDX-FileCopyrightText: 2021 foamyguy
#
# SPDX-License-Identifier: MIT

import requests
import json
import urllib.request


def find_data_asset(assets):
    for i, asset in enumerate(assets):
        if asset["name"].endswith(".json"):
            return i
    return None


resp_obj = requests.get(
    "https://api.github.com/repos/adafruit/Adafruit_CircuitPython_Bundle/releases/latest"
)
resp_json = json.loads(resp_obj.content)

data_json_index = find_data_asset(resp_json["assets"])
data_json_url = resp_json["assets"][data_json_index]["browser_download_url"]

urllib.request.urlretrieve(data_json_url, "latest_bundle_data.json")
