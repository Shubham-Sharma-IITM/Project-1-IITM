import requests
from urllib.parse import unquote
import json


with open("cookies.txt", "r") as file:
    cookie = file.read().strip()
headers = {
    "cookie": cookie
}
url1 = "https://discourse.onlinedegree.iitm.ac.in/search.json?q=%23courses%3Atds-kb%20before%3A2025-04-14%20after%3A2025-01-01%20order%3Alatest&page=1"
url2 = "https://discourse.onlinedegree.iitm.ac.in/search.json?q=%23courses%3Atds-kb%20before%3A2025-04-14%20after%3A2025-01-01%20order%3Alatest&page=2"
url3 = "https://discourse.onlinedegree.iitm.ac.in/search.json?q=%23courses%3Atds-kb%20before%3A2025-04-14%20after%3A2025-01-01%20order%3Alatest&page=3"
# Send GET request with cookies
response1 = requests.get(url1, headers=headers)
response2 = requests.get(url2, headers=headers)
response3 = requests.get(url3, headers=headers)
# Write response content to a file
with open("response1.json", "w") as file:
    json.dump(response1.json(),file, indent=4)
with open("response2.json", "w") as file:
    json.dump(response2.json(),file, indent=4)
with open("response3.json", "w") as file:
    json.dump(response3.json(),file, indent=4)
print("Response written to response.json")
