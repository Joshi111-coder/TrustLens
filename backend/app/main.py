from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.database import init_db
from app.routes.health import router as health_router
from app.routes.analyze import router as analyze_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables on startup
    init_db()
    print("[TrustLens] SQLite Database initialized successfully.")
    yield

app = FastAPI(
    title="TrustLens API",
    description="AI-powered financial content verification assistant for first-time investors",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")

@app.get("/")
def root():
    return {
        "app": "TrustLens API",
        "tagline": "Understand before you trust.",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

