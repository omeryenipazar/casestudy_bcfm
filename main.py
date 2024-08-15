from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "BC4M"}

@app.get("/health")
def read_health():
    return {"status": "healthy"}

class Item(BaseModel):
    name: str
    value: str

@app.post("/data")
def receive_data(item: Item):
    return item
