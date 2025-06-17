import os
import json
from bs4 import BeautifulSoup

def remove_html_tags(text):
    return BeautifulSoup(text, "html.parser").get_text(separator=" ")

def clean_json_file(file_path):
    print(f"Cleaning file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for post in data.get("posts", []):
            original_text = post.get("text", "")
            clean_text = remove_html_tags(original_text)
            post["text"] = clean_text.strip()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Cleaned: {file_path}")

    except Exception as e:
        print(f"❌ Failed to process {file_path}: {e}")

def clean_folder(folder_path):
    print(f"\n🔍 Cleaning HTML tags in folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            clean_json_file(file_path)
    print("\n✅ All files cleaned.")

# 🔁 Replace with your actual folder path
if __name__ == "__main__":
    folder_path = r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\longposts"
    clean_folder(folder_path)
