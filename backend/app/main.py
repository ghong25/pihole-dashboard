import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.services import device_db, scheduler
from app.routers import dashboard, devices, domains, logs, blocking


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await device_db.init_db()
    await scheduler.init()
    yield
    # Shutdown
    await scheduler.shutdown()


app = FastAPI(title="Pi-hole Dashboard", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(dashboard.router)
app.include_router(devices.router)
app.include_router(domains.router)
app.include_router(logs.router)
app.include_router(blocking.router)

# Mount frontend static files if the dist directory exists
if os.path.isdir(settings.static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(settings.static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the Vue SPA for any non-API route."""
        file_path = os.path.join(settings.static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(settings.static_dir, "index.html"))
