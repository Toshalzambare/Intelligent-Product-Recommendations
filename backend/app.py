from fastapi import FastAPI

app = FastAPI(title="CrediMetrics Backend")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Backend is running"
    }


