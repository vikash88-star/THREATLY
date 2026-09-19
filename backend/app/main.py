from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.analysis import router as analysis_router
from app.api.investigation import router as investigation_router
from app.api.reports import router as reports_router
from app.core.security import limiter


app = FastAPI(
    title="Threatly API",
    description="AI-Powered Digital Threat Investigation Platform",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analysis_router)
app.include_router(investigation_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {
        "message": "Threatly API is running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": "Threatly",
    }