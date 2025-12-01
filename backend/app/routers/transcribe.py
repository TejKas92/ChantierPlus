from fastapi import APIRouter, UploadFile, File, HTTPException
import openai
import os
from pydantic import BaseModel

router = APIRouter(
    prefix="/api",
    tags=["transcribe"]
)

class TranscriptionResponse(BaseModel):
    text: str

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Mock response if no API key
        return {"text": "Ceci est une transcription simulée car la clé API OpenAI est manquante. Installer une prise électrique supplémentaire dans le salon."}

    client = openai.OpenAI(api_key=api_key)
    
    # Save temp file
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        buffer.write(await file.read())

    try:
        with open(temp_filename, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        return {"text": transcript.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
