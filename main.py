from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "BC4M"}

@app.get("/health")
def read_health():
    return {"status": "healthy"}

@app.post("/data")
def receive_data(data: Dict[str, Any]):
    return data
