from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class ResetRequest(BaseModel):
    task: str = 'easy'

@app.post('/reset1')
def reset1(req: ResetRequest):
    return {}

@app.post('/reset2')
def reset2(req: Optional[ResetRequest] = None):
    return {}

@app.post('/reset3')
def reset3(req: dict = None):
    return {}

client = TestClient(app)
print('1', client.post('/reset1').json())
print('2', client.post('/reset2').json())
print('3', client.post('/reset3').json())
print('4', client.post('/reset1', json=None).json())
print('5', client.post('/reset2', json=None).json())
print('6', client.post('/reset3', json=None).json())
