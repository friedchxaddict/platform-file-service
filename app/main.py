from fastapi import FastAPI, UploadFile, File 
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
UPLOAD_DIR = Path("/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


#Health endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

#Upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    safe_name = Path(file.filename).name
    filepath = UPLOAD_DIR / safe_name

    filepath.write_bytes(content)

    logger.info(f"Uploaded file: {safe_name}, size={len(content)} bytes")

    return {
        "filename": safe_name,
        "size_bytes": len(content),
        "saved_to": str(filepath)
    } # Return the file name and size

#List files endpoint
@app.get("/files")
def list_files():
    if not UPLOAD_DIR.exists():
        return {"files": []}

    files = sorted(
        [p.name for p in UPLOAD_DIR.iterdir() if p.is_file()]
    )
    return {"files": files} # Return the list of uploaded files

@app.get("/files/{filename}")
def get_file(filename: str):
    filepath = UPLOAD_DIR / filename

    # Prevent weird paths like ../../etc/passwd
    try:
        filepath.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=str(filepath), filename=filename)

@app.delete("/files/{filename}")
def delete_file(filename: str):
    filepath = UPLOAD_DIR / filename

    # Prevent weird paths like ../../etc/passwd
    try:
        filepath.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    filepath.unlink()
    logger.info(f"Deleted file: {filename}")

    return {"deleted": filename}