import os
import json

def transform_json_structure(file_path):
    print(f"Processing: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        transformed_posts = []
        for post in data.get("posts", []):
            cooked = post.get("cooked", "")
            post_url = post.get("post_url", "")
            full_url = f"https://discourse.onlinedegree.iitm.ac.in{post_url}"
            transformed_posts.append({
                "text": cooked,
                "url": full_url
            })

        new_data = {"posts": transformed_posts}

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        print(f"Saved: {file_path}")

    except Exception as e:
        print(f"Failed processing {file_path}: {e}")

def process_folder(folder_path):
    print(f"\n🔍 Scanning folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            transform_json_structure(file_path)
    print("\nAll files processed.")

# Change path to your actual JSON folder
if __name__ == "__main__":
    folder_path = r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\longposts"
    process_folder(folder_path)
