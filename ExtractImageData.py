
import os
import json
import requests
import time
from bs4 import BeautifulSoup
from PIL import Image
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# 1. Configure Google Gemini API
GOOGLE_API_KEY = "AIzaSyA8IkPvKPHYS9AFLV5OLyHHx0w_tjuu2WI"   # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 2. Analyze image using Gemini with retry on 429 and sleep to limit request rate
def analyze_image_with_llm(image_path, max_retries=5):
    for attempt in range(max_retries):
        try:
            time.sleep(4)  # Enforce 15 requests/minute rate limit
            print(f"Analyzing image: {image_path}")
            img = Image.open(image_path)
            response = model.generate_content(["Describe this image:" , img])
            result = response.text if hasattr(response, 'text') else str(response)
            print("Image analysis completed.")
            return result
        except ResourceExhausted as e:
            if 'quota' in str(e).lower() or '429' in str(e):
                wait_time = 60
                print(f"Quota exceeded. Waiting {wait_time} seconds before retrying... (Attempt {attempt+1})")
                time.sleep(wait_time)
            else:
                print(f"Quota error not retryable: {e}")
                return f"Failed to analyze image: {e}"
        except Exception as e:
            print(f"Failed to analyze image {image_path}: {e}")
            return f"Failed to analyze image: {e}"
    return "Image analysis failed after retries."

def extract_image_urls(html):
    soup = BeautifulSoup(html, 'html.parser')
    image_urls = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if 'user_avatar' not in src and 'emoji' not in src:
            image_urls.append(src)
    return image_urls

# 4. Download image from URL
def download_image(url, download_dir):
    try:
        print(f"Downloading image: {url}")
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            os.makedirs(download_dir, exist_ok=True)
            filename = os.path.join(download_dir, os.path.basename(url.split("?")[0]))
            with open(filename, 'wb') as out_file:
                for chunk in response.iter_content(1024):
                    out_file.write(chunk)
            print(f"Image saved to: {filename}")
            return filename
        else:
            print(f"Failed to download image (status code {response.status_code}): {url}")
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
    return None

# 5. Process a single JSON file
def process_json_file(file_path, download_dir):
    print(f"\nProcessing file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON: {file_path}\nError: {e}")
        return

    updated = False
    for index, post in enumerate(data.get("posts", [])):
        html_text = post.get("text", "")
        image_urls = extract_image_urls(html_text)

        if image_urls:
            print(f"Found {len(image_urls)} image(s) in post {index + 1}.")
            descriptions = []
            for img_url in image_urls:
                local_image = download_image(img_url, download_dir)
                if local_image:
                    description = analyze_image_with_llm(local_image)
                    descriptions.append(description)
            post["image_description"] = descriptions  # Always a list
            updated = True
        else:
            print(f"No valid (non-avatar) images in post {index + 1}.")

    if updated:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated JSON saved: {file_path}")
        except Exception as e:
            print(f"Error saving updated JSON to {file_path}: {e}")

# 6. Process all JSON files in the folder
def process_folder(folder_path, download_dir='downloaded_images'):
    print(f"Starting processing of folder: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            full_path = os.path.join(folder_path, filename)
            process_json_file(full_path, download_dir)
    print("All files processed.")

# 7. Run the script
if __name__ == "__main__":
    folder_path = r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\posts-cleaned\New Folder\New Folder"
    process_folder(folder_path)
