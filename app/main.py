from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from app.tts import generate_audio
from fastapi.templating import Jinja2Templates
import mimetypes

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get absolute path of current file
AUDIO_DIR = os.path.join(BASE_DIR, "static/audio")  # Absolute path to audio folder

# When running in Docker, static files are in /app directory
STATIC_DIR = "/app/app/static" if os.path.exists("/app") else "app/static"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Serve static files (CSS, etc.)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup templates
templates = Jinja2Templates(directory="/app/app/templates" if os.path.exists("/app") else "app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/text-to-speech/")
async def text_to_speech(request: Request, text: str = Form(...), voice: str = Form("female")):
    file_name = generate_audio(text, voice)
    # Return both file name and URL
    return templates.TemplateResponse("index.html", {
        "request": request,
        "file_url": f"/static/audio/{file_name}",
        "file_name": file_name
    })

@app.get("/static/audio/{file_name}")
async def download_audio(file_name: str):
    # Use AUDIO_DIR for file path to ensure correct directory is used
    file_path = os.path.join(AUDIO_DIR, file_name)
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="audio/mpeg",
            background=asyncio.create_task(delete_file_later(file_path))
        )

    # Log the error for debugging
    print(f"File not found: {file_path}")
    raise HTTPException(status_code=404, detail="File not found")

async def delete_file_later(file_path: str):
    await asyncio.sleep(30)  # Wait 30 seconds before deleting
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Successfully deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")
