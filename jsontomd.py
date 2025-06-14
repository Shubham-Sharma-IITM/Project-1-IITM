import os
import json

def convert_json_to_md(json_folder):
    markdown_folder = os.path.join(json_folder, "markdowns")
    os.makedirs(markdown_folder, exist_ok=True)

    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            json_path = os.path.join(json_folder, filename)
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    print(f"Skipping {filename}, failed to parse JSON: {e}")
                    continue

            md_lines = [f"# {filename}\n"]
            posts = data.get("posts", [])
            for i, post in enumerate(posts):
                md_lines.append(f"## Post {i + 1}\n")
                text = post.get("text", "").strip()
                url = post.get("url", "").strip()
                images = post.get("image_description", [])

                md_lines.append(text)
                if url:
                    md_lines.append(f"\n🔗 [Post URL]({url})\n")

                if isinstance(images, list) and images:
                    md_lines.append("\n### 🖼️ Image Descriptions:\n")
                    for idx, desc in enumerate(images, 1):
                        md_lines.append(f"- {desc.strip()}")
                elif isinstance(images, str):
                    md_lines.append(f"\n### 🖼️ Image Description:\n- {images.strip()}")

                md_lines.append("\n---\n")

            # Write the markdown file
            md_filename = filename.replace(".json", ".md")
            md_path = os.path.join(markdown_folder, md_filename)
            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write("\n".join(md_lines))
            
            print(f"✅ Converted: {filename} → {md_filename}")

    print("\nAll JSON files converted to Markdown.")

# Example usage
if __name__ == "__main__":
    folder_path = r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\jsons-without-html"
    convert_json_to_md(folder_path)
