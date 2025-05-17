from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List
from pydantic import BaseModel
from src.dataIngestion import dataReader
from src.ragPipeline import ragGenerator
import json
import os
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

subprocess.run('rm -rf ./docs',shell=True)

UPLOAD_FOLDER = './docs'
DOWNLOAD_FOLDER = './outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class Question(BaseModel):
    question: str

@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    for file in files:
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        contents = await file.read()
        with open(file_location, "wb") as f:
            f.write(contents)
    ragGenerator().embeddingPipeline()
    return {"message": "All files ingested."}

@app.post("/chat_answer")
async def answer(q: Question):
    responses = ragGenerator().ragsPipeline(questions=q.question)
    return {"answer": responses}

@app.post("/batch_answer")
async def answer_from_file(file: UploadFile = File(...)):
    contents = await file.read()
    payload = json.loads(contents)
    questions = payload.get("questions", [])

    if not questions or not isinstance(questions, list):
        return {"error": "JSON must contain a 'questions' list."}
    
    results = []
    for question in questions:
        responses = ragGenerator().ragsPipeline(questions=question)
        results.append({"question":question, "answer":responses})

    with open(os.path.join(DOWNLOAD_FOLDER,'answer.json'),'w') as f:
        json.dump(results, f, indent=2)

    return results