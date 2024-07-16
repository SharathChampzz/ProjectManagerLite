from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

#### Load Environment Variables - START ####
from dotenv import load_dotenv
load_dotenv()

help_str = """
Required Environment Variables:
- UPLOAD_DIRECTORY: The directory where the uploaded files will be stored. (Usage: C:\\uploads)
- ALLOW_ORIGIN: The URL of the frontend app that will be using this service. (Usage: http://localhost:3000,http://localhost:3001)
"""

UPLOAD_DIRECTORY = os.getenv('UPLOAD_DIRECTORY')
ALLOW_ORIGIN = os.getenv('ALLOW_ORIGIN')

print(f"UPLOAD_DIRECTORY set to => {UPLOAD_DIRECTORY}")
print(f"ALLOW_ORIGIN set to => {ALLOW_ORIGIN}")

if not all([UPLOAD_DIRECTORY, ALLOW_ORIGIN]):
    print(help_str)
    raise ValueError('Required environment variables are not set.')

### Load Environment Variables - END ###

app = FastAPI()
allowed_origin = ALLOW_ORIGIN.split(",")
print(f"Allowed Origin set to => {allowed_origin}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = Path(UPLOAD_DIRECTORY) / file.filename
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())
    return {"file_url": f"/files/{file.filename}"}

# This is just a helper endpoint to see the uploaded files in the browser
@app.get("/files/")
async def list_files():
    files = [f'<a href="/files/{file.name}" target="_blank">{file.name}</a><br>' for file in Path(UPLOAD_DIRECTORY).iterdir()]
    html_content = "\n".join(files)
    return HTMLResponse(content=html_content)

@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = Path(UPLOAD_DIRECTORY) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
