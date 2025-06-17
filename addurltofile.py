import os
import re

folder_path = r"C:\Users\shris\OneDrive\Desktop\Shubham\Tools in Data Science\project 1\dated-clone\tools-in-data-science-public-edited"
sidebar_path = os.path.join(folder_path, "_sidebar.md")
with open(sidebar_path, "r", encoding="utf-8") as sidebar_file:
    lines = sidebar_file.readlines()
pattern = re.compile(r"\[.*?\]\((.+?)\.md\)")

for line in lines:
    match = pattern.search(line)
    if match:
        topic_name = match.group(1).strip()  # Just the file name without `.md`
        filename = topic_name + ".md"
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            with open(file_path, "a", encoding="utf-8") as topic_file:
                topic_file.write(f"\n\n[Post URL](https://tds.s-anand.net/#/{topic_name})\n")
            print(f"Updated: {filename}")
        else:
            print(f"File not found: {filename}")
