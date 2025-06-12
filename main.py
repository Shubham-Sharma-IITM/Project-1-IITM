from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import base64
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    question: str
    image: Optional[str] = None


class Link(BaseModel):
    url: str
    text: str


class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

token = os.getenv("AI_PIPE_TOKEN") 


@app.post("/api/", response_model=AnswerResponse)
async def receive_question(data: RequestData):
    question = data.question
    image_data = data.image
    print("Checking token", token)

    # You can later plug in actual model logic here. For now, dummy response.
    if image_data:
        try:
            _ = base64.b64decode(image_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")

    # This is a hardcoded mock answer - you can replace it with AI model logic
    return AnswerResponse(
        answer="You must use `gpt-3.5-turbo-0125`, even if the AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly for this question.",
        links=[
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
                "text": "Use the model that’s mentioned in the question."
            },
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3",
                "text": "My understanding is that you just have to use a tokenizer, similar to what Prof. Anand used, to get the number of tokens and multiply that by the given rate."
            }
        ]
    )
