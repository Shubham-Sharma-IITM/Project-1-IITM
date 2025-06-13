import json
import requests
import os

with open("response3.json", "r") as file:
    data = json.load(file)

with open("cookies.txt", "r") as file:
    cookie = file.read().strip()
headers = {
    "cookie": cookie
}

for topic in data.get("topics", []):
    topic_id = topic.get("id")
    slug = topic.get("slug")
    url = f"https://discourse.onlinedegree.iitm.ac.in/t/{slug}/{topic_id}.json"
    print(f"ID: {topic_id}, Slug: {slug}")
    response = requests.get(url, headers=headers)
    json_data = response.json()
    post_ids = json_data.get("post_stream", {}).get("stream", [])
    base_url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}/posts.json?"
    query_params = '&'.join([f"post_ids[]={pid}" for pid in post_ids])
    final_url = base_url + query_params
    final_response = requests.get(final_url, headers=headers)
    filepath = os.path.join("posts", f"{slug}.json")
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(final_response.json(), file, indent=4)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for: {final_url}")
        continue
    
