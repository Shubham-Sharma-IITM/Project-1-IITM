import os
import json
from bs4 import BeautifulSoup

def clean_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # Replace <img alt="..."> with its alt text
    for img in soup.find_all("img"):
        if img.has_attr("alt"):
            print("Replacing <img> with alt text:", img['alt'])
            img.replace_with(f"[EMOJI {img['alt']}]")

    for span in soup.find_all("span"):
        span.unwrap()

    for a in soup.find_all("a"):
        a.unwrap()

    return soup.get_text(separator="\n", strip=True)

def process_json_file(input_path, output_path):
    print(f"Processing file: {os.path.basename(input_path)}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for idx, post in enumerate(data.get("posts", [])):
        print(f"  Cleaning post #{idx + 1}")
        html_text = post.get("text", "")
        clean_text = clean_html(html_text)

        image_desc = post.get("image_description")
        if image_desc:
            print(f"  Adding image description for post #{idx + 1}")
            if isinstance(image_desc, list):
                image_desc_text = "\n".join(image_desc)
            else:
                image_desc_text = str(image_desc)
            clean_text += f"\n\nImage Description:\n{image_desc_text.strip()}"

        post["text"] = clean_text

        url = post.get("url", "")
        if "//t/" in url:
            fixed_url = url.replace("//t/", "/t/")
            print(f"  Fixed URL: {fixed_url}")
            post["url"] = fixed_url

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  File saved.\n")

def process_folder(input_folder):
    output_folder = os.path.join(os.path.dirname(input_folder), "jsons-without-html")
    os.makedirs(output_folder, exist_ok=True)

    print(f"Starting processing of folder: {input_folder}")
    print(f"Output folder: {output_folder}\n")

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            process_json_file(input_path, output_path)

    print("All files processed and saved.")

# Run the script
if __name__ == "__main__":
    input_folder = r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\posts-cleaned-copy"
    process_folder(input_folder)
