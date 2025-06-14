import re
import json
from pathlib import Path
import numpy as np
def extract_chunk_info(chunks, sidebar_path):
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        sidebar_content = f.read()

    result = []
    url_base = "https://tds.s-anand.net/#/"

    for chunk in chunks:
        chunk_str = str(chunk)
        entry = {"text": "", "url": ""}

        # Case 1: [Post URL](...)
        post_url_match = re.search(r"\[Post URL\]\((.*?)\)", chunk_str)
        if post_url_match:
            entry["url"] = post_url_match.group(1)
            entry["text"] = chunk_str.replace("\n", " ").split("[Post URL]")[0].strip()

        else:
            # Case 2: Markdown heading like ## Containers: Docker, Podman
            heading_match = re.search(r"^##\s+(.+)", chunk_str)
            if heading_match:
                heading_text = heading_match.group(1).strip()
                # Search sidebar for [Heading Text](somefile.md)
                pattern = re.escape(f"[{heading_text}]") + r"\(([^)]+\.md)\)"
                sidebar_match = re.search(pattern, sidebar_content)
                if sidebar_match:
                    md_file = sidebar_match.group(1).strip()
                    url_path = md_file.replace(".md", "")
                    entry["url"] = f"{url_base}{url_path}"
            entry["text"] = chunk_str.replace("\n", " ").strip()

        result.append(entry)

    return result

chunks = [
    np.str_('## Containers: Docker, Podman\n\n[Docker](https://www.docker.com/) and [Podman](https://podman.io/) are containerization tools that package your application and its dependencies into a standardized unit for software development and deployment.\n\nDocker is the industry standard. Podman is compatible with Docker and has better security (and a slightly more open license). In this course, we recommend Podman but Docker works in the same way.\n\nInitialize the container engine:\n\n```bash\npodman machine init\npodman machine start\n```\n\nCommon Operations. (You can use `docker` instead of `podman` in the same way.)\n\n```bash\n# Pull an image\npodman pull python:3.11-slim\n\n# Run a container\npodman run -it python:3.11-slim\n\n# List containers\npodman ps -a\n\n# Stop container\npodman stop container_id\n\n# Scan image for vulnerabilities\npodman scan myapp:latest\n\n# Remove container\npodman rm container_id\n\n# Remove all stopped containers\npodman container prune\n```'),
    
    np.str_('## Post 21\n\nThank you, Sir!\nWhat is the Docker image URL? It should look like:\nhttps://hub.docker.com/repository/docker/$USER/$REPO/general\nIf I use Podman, will the answer be correct assuming I have done all steps correctly?\n\n🔗 [Post URL](https://discourse.onlinedegree.iitm.ac.in/t/ga2-deployment-tools-discussion-thread-tds-jan-2025/161120/22)\n\n\n---'),

    np.str_('The overall purpose of the image is to guide users through the process of containerizing an application (likely named `py-hello`), building it, running it locally, and then deploying it to Docker Hub for sharing or later deployment elsewhere.  The instructions use `podman`, a daemonless container engine.\n\n🔗 [Post URL](https://discourse.onlinedegree.iitm.ac.in/t/ga2-deployment-tools-discussion-thread-tds-jan-2025/161120/158)')
]


sidebar_path = "_sidebar.md"

output = extract_chunk_info(chunks, sidebar_path)

# To print or save as JSON:
print(json.dumps(output, indent=2))
