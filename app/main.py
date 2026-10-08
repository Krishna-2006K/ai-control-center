from fastapi import FastAPI

app = FastAPI(title="AICC — AI Control Center", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aicc"}
