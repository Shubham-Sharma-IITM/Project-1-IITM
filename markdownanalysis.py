import os
import re
import time
import requests
from PIL import Image
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# === Setup Gemini ===
GOOGLE_API_KEY = "AIzaSyD3CbeVTor9mnSnKulgmbHQ0u-VgiApuso"  # Replace this with your actual key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# === Remove HTML tags from markdown ===
def remove_html_tags(text):
    return BeautifulSoup(text, "html.parser").get_text()

# === Extract image URLs from markdown, HTML, and plain text ===
def extract_image_urls(text):
    all_urls = re.findall(r'https?://[^\s\)>\"]+', text)
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff')
    image_urls = [url for url in all_urls if url.lower().split("?")[0].endswith(image_extensions)]
    return image_urls

# === Download image from URL ===
def download_image(url, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    filename = os.path.basename(url.split("?")[0])
    local_path = os.path.join(target_dir, filename)
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {local_path}")
            return local_path
        else:
            print(f"Failed to download {url} (status {response.status_code})")
    except Exception as e:
        print(f"Download error: {url} - {e}")
    return None

# === Analyze image with Gemini (retry on quota) ===
def analyze_image_with_llm(image_path, max_retries=5):
    for attempt in range(max_retries):
        try:
            time.sleep(4)  # Rate limit
            img = Image.open(image_path)
            response = model.generate_content(["Describe this image:", img])
            return response.text.strip() if hasattr(response, 'text') else str(response)
        except ResourceExhausted as e:
            if 'quota' in str(e).lower() or '429' in str(e):
                print(f"Quota exceeded. Retry in 60s... (Attempt {attempt+1})")
                time.sleep(60)
            else:
                return f"Quota error: {e}"
        except Exception as e:
            return f"Error analyzing image: {e}"
    return "Image analysis failed after retries."

# === Process a single Markdown file ===
def process_markdown_file(md_path):
    print(f"\n📄 Processing: {md_path}")
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Failed to read: {md_path}\nError: {e}")
        return

    # Clean HTML
    content_cleaned = remove_html_tags(content)

    # Extract image URLs
    image_urls = extract_image_urls(content_cleaned)
    if not image_urls:
        print("ℹ️ No image URLs found.")
        return

    # Prepare image folder
    md_dir = os.path.dirname(md_path)
    md_name = os.path.splitext(os.path.basename(md_path))[0]
    image_dir = os.path.join(md_dir, f"image-for-{md_name}")

    # Analyze and describe images
    descriptions = []
    for url in image_urls:
        img_path = download_image(url, image_dir)
        if img_path:
            desc = analyze_image_with_llm(img_path)
            descriptions.append((url, desc))

    # Inject image descriptions
    content_cleaned += "\n\n## image_description\n"
    for url, desc in descriptions:
        content_cleaned += f"\n**Image:** {url}\n\n{desc}\n"

    # Save back
    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content_cleaned)
        print(f"✅ Updated: {md_path}")
    except Exception as e:
        print(f"❌ Failed to write: {md_path}\nError: {e}")

# === Recursively process all Markdown files ===
def process_folder(folder_path):
    print(f"🚀 Starting folder scan: {folder_path}")
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.md'):
                full_path = os.path.join(root, file)
                process_markdown_file(full_path)
    print("✅ All Markdown files processed.")

# === Entry point ===
if __name__ == "__main__":
    base_folder = r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\dated-clone\tools-in-data-science-public - Copy"  # 🔁 Change this
    process_folder(base_folder)
