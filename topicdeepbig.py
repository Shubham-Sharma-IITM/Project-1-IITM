import json
import requests
import os

# Load topics and cookie
data = {
    "topics": [
        {
            "id": 169029,
            "slug": "project-2-tds-solver-discussion-thread"
        },
        {
            "id": 164277,
            "slug": "project-1-llm-based-automation-agent-discussion-thread-tds-jan-2025"
        },
    ]
}
with open("cookies.txt", "r") as file:
    cookie = file.read().strip()

headers = {
    "cookie": cookie
}

# Ensure posts/ directory exists
os.makedirs("posts", exist_ok=True)

def chunk_list(lst, size):
    """Yield successive chunks from a list."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

for topic in data.get("topics", []):
    topic_id = topic.get("id")
    slug = topic.get("slug")
    print(f"ID: {topic_id}, Slug: {slug}")

    # Step 1: Get all post_ids for the topic
    topic_url = f"https://discourse.onlinedegree.iitm.ac.in/t/{slug}/{topic_id}.json"
    response = requests.get(topic_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch topic: {topic_url}")
        continue

    json_data = response.json()
    post_ids = json_data.get("post_stream", {}).get("stream", [])

    # Step 2: Chunk post_ids
    all_posts = []
    for chunk in chunk_list(post_ids, 100):  # adjust chunk size if needed
        query_params = '&'.join([f"post_ids[]={pid}" for pid in chunk])
        chunk_url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}/posts.json?{query_params}"
        chunk_response = requests.get(chunk_url, headers=headers)
        if chunk_response.status_code != 200:
            print(f"Chunk failed: {chunk_url} — {chunk_response.status_code}")
            continue

        chunk_json = chunk_response.json()
        all_posts.extend(chunk_json.get("post_stream", {}).get("posts", []))

    # Step 3: Save merged posts to file
    filepath = os.path.join("posts", f"{slug}.json")
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump({"posts": all_posts}, file, indent=4)
