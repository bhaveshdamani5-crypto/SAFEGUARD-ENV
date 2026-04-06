from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api import app as api_app
import uvicorn
import os

# Mount the API app under /api is already handled in backend/api.py
# We will use this app to mount the frontend and include the api router

app = FastAPI(title="SafeGuard-Env Main App")

# Include API routes
app.mount("/api", api_app)

# Serve Frontend
os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)
