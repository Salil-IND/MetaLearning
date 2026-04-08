from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata like SLA, tags, or threat-level.")

class Observation(BaseModel):
    inbox: List[Email]
    archived: List[Email]
    replied: List[Email]
    forwarded: List[Email]
    spam: List[Email]
    escalated: List[Email]
    pending_info: List[Email]

class Action(BaseModel):
    action_type: str = Field(..., description="'reply', 'forward', 'archive', 'mark_spam', 'request_info', or 'escalate'")
    email_id: str
    response_text: Optional[str] = None
    forward_to: Optional[str] = None
    priority_level: str = Field(default="normal", description="'urgent', 'normal', or 'low'")

class State(BaseModel):
    step_count: int
    max_steps: int
    score: float
    is_done: bool
    observation: Observation
