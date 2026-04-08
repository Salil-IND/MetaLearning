from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from env.environment import EmailTriageEnv

app = FastAPI()
env = EmailTriageEnv()

@app.get("/")
async def root():
    return {
        "name": "Email Triage OpenEnv",
        "status": "running",
        "instructions": "Use POST /reset and POST /step to interact with this environment."
    }


class ResetRequest(BaseModel):
    task: str = "easy"

class StepRequest(BaseModel):
    action: Dict[str, Any] = Field(default_factory=dict)

@app.post("/reset")
async def reset_env(req: Optional[ResetRequest] = None):
    task_name = req.task if req else "easy"
    obs, info = await env.reset(task_name)
    return {
        "observation": obs.model_dump(),
        "info": info
    }

@app.post("/step")
async def step_env(req: StepRequest):
    obs, reward, done, info = await env.step(req.action)
    return {
        "observation": obs.model_dump() if obs else None,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }

@app.get("/state")
async def get_state():
    state = env.state()
    return state.model_dump()
