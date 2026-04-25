from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .models import init_db

# Initialize FastAPI app
app = FastAPI(
    title="Secure P2P File Sharing API",
    description="REST API wrapper for secure peer-to-peer file transfer system",
    version="1.0.0"
)

# Initialize database on startup
init_db()

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["file-transfer"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Secure P2P File Sharing API",
        "version": "1.0.0",
        "description": "REST API for secure peer-to-peer file transfer",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health/",
            "send_file": "/api/v1/send-file/"
        },
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
