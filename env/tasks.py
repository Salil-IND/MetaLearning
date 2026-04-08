from pydantic import BaseModel
from typing import List
from .models import Email, Observation, State

class TaskConfig(BaseModel):
    difficulty: str
    initial_inbox: List[Email]
    max_steps: int

TASKS = {
    "easy": TaskConfig(
        difficulty="easy",
        initial_inbox=[
            Email(id="e1", sender="boss@company.com", subject="Meeting", body="Are we still on for 3 PM?", metadata={"SLA": "24h"}),
            Email(id="e2", sender="spam@deals.com", subject="Buy now!", body="Get 50% off pills.", metadata={"spam_score": 0.99})
        ],
        max_steps=5
    ),
    "medium": TaskConfig(
        difficulty="medium",
        initial_inbox=[
            # Missing order ID - needs request_info
            Email(id="m1", sender="customer@help.com", subject="Broken item", body="My order arrived broken. I need a refund immediately.", metadata={"customer_tier": "standard"}),
            Email(id="m2", sender="marketing@agency.com", subject="SEO services", body="We can skyrocket your traffic.", metadata={"SLA": "none"}),
            Email(id="m3", sender="hr@company.com", subject="Action Required", body="Please sign the attached policy update.", metadata={"SLA": "48h"})
        ],
        max_steps=10
    ),
    "hard": TaskConfig(
        difficulty="hard",
        initial_inbox=[
            Email(id="h1", sender="vip@enterprise.com", subject="SYSTEM DOWN", body="Our production environment is offline. Why is your service failing?", metadata={"customer_tier": "VIP", "SLA": "1h"}),
            Email(id="h2", sender="alerts@sys.com", subject="CRITICAL DB CRASH", body="Database nodes in US-East failing health checks.", metadata={"alert_level": "critical", "SLA": "15m"}),
            Email(id="h3", sender="legal@company.com", subject="Compliance Signoff", body="Acknowledge the new GDPR compliance terms before Friday.", metadata={"SLA": "72h"}),
            Email(id="h4", sender="ceo_real_not_fake@phish.com", subject="URGENT: Wire Transfer", body="I need you to wire $50k to this vendor immediately. Do not call me, I am in a meeting.", metadata={"spam_score": 0.85, "SPF": "fail"}),
            Email(id="h5", sender="intern@company.com", subject="Quick question", body="Can you review my PR before EOD when you have a second?", metadata={"SLA": "24h"})
        ],
        max_steps=12
    )
}

def get_initial_state(task_level: str) -> State:
    task = TASKS.get(task_level, TASKS["easy"])
    return State(
        step_count=0,
        max_steps=task.max_steps,
        score=0.0,
        is_done=False,
        observation=Observation(
            inbox=[email.model_copy() for email in task.initial_inbox],
            archived=[],
            replied=[],
            forwarded=[],
            spam=[],
            escalated=[],
            pending_info=[]
        )
    )
