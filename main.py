from fastapi import FastAPI, Response, status
from typing import Dict, Any

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "BC4M"}

@app.get("/health")
def read_health(response: Response):
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "unhealthy"}

@app.post("/data")
def receive_data(data: Dict[str, Any]):
    return data