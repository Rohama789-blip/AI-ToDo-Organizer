
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import organize_tasks
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI To-Do List Organizer",
    description="Organize tasks using Groq AI and LangGraph",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TodoRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "AI To-Do List Organizer API is running!",
        "docs": "/docs",
    }


@app.post("/organize")
def organize(request: TodoRequest):
    try:
        result = organize_tasks(request.message)
        return {"result": result}

    except Exception as error:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Task organization failed: {str(error)}",
        )
