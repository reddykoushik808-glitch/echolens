import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env BEFORE anything else imports env vars
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes import upload, dashboard, agent

app = FastAPI(
    title="EchoLens API",
    description="Customer feedback intelligence that remembers",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(agent.router, prefix="/api", tags=["Agent"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "EchoLens"}

# Path to frontend directory (resolved to absolute)
FRONTEND_DIR = str(Path(__file__).resolve().parent.parent / "frontend")

if os.path.exists(FRONTEND_DIR):
    # Serve HTML pages
    @app.get("/")
    async def read_root():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{page_name}.html")
    async def read_html(page_name: str):
        file_path = os.path.join(FRONTEND_DIR, f"{page_name}.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    # Mount static file directories AFTER explicit routes
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
