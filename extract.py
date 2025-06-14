import google.generativeai as genai
from PIL import Image

# Step 1: Configure API
GOOGLE_API_KEY = "AIzaSyDXMMPupYfaDe2bjXebHnlOUVbMd-O_mxI"
genai.configure(api_key=GOOGLE_API_KEY)

# Step 2: Use a newer model
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Step 3: Analyze image
def analyze_image_with_llm(image_path):
    try:
        print(f"Analyzing image: {image_path}")
        image = Image.open(image_path)

        response = model.generate_content(
            [ "Describe this image in detail", image ]
        )

        result = response.text if hasattr(response, 'text') else str(response)
        print("Image analysis completed.")
        return result

    except Exception as e:
        print(f"Failed to analyze image {image_path}: {e}")
        return f"Failed to analyze image: {e}"

# Step 4: Test it
description = analyze_image_with_llm("./white_flag.png")
print("LLM Output:", description)
