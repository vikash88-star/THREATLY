from fastapi import FastAPI

app = FastAPI(
    title="Threatly API",
    description="AI-Powered Digital Threat Investigation Platform",
    version="0.1.0",
)


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