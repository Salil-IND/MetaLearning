---
title: Email Triage OpenEnv
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# Email Triage OpenEnv

A real-world OpenEnv simulator that tests an agent's ability to efficiently manage an inbox through replying, forwarding, archiving, and identifying spam with constraints and SLA tracking.

## Structure
- `env/`: Environment logic and pydantic models
- `server/`: FastAPI server wrapper
- `inference.py`: Standard inference script connecting to OpenAI LLMs.

## Deployment (Hugging Face Spaces Compatible)
Run with Docker:
`docker build -t email-env .`
`docker run -p 7860:7860 email-env`

Validate:
`openenv validate`

Start testing APIs on 0.0.0.0:7860.
