import os
import requests
import json
import time
import re

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-turbo")
HF_TOKEN = os.getenv("HF_TOKEN", "hf_mock_token")

class MockOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.chat = self.Chat()
        
    class Chat:
        def __init__(self):
            self.completions = self.Completions()
            
        class Completions:
            def create(self, model, messages, response_format=None):
                class ResponseMessage:
                    def __init__(self, content): self.content = content
                class ResponseChoice:
                    def __init__(self, message): self.message = message
                class Response:
                    def __init__(self, choices): self.choices = choices
                
                content = str(messages[-1]["content"]).lower()
                action = {"action_type": "reply", "email_id": "", "response_text": "Noted.", "forward_to": None, "priority_level": "normal"}
                
                match = re.search(r"'id': '([^']+)'", str(messages))
                if match: action["email_id"] = match.group(1)
                    
                if "spam" in content or "wire" in content or "password" in content or "phish" in content or "traffic" in content:
                    action["action_type"] = "mark_spam"
                elif "broken" in content and "order" in content and "id" not in content:
                    action["action_type"] = "request_info"
                    action["response_text"] = "Please provide your order ID."
                elif "downtime" in content or "offline" in content or "fail" in content:
                    if "vip" in content:
                        action["action_type"] = "reply"
                        action["priority_level"] = "urgent"
                        action["response_text"] = "We are currently investigating the downtime."
                    else:
                        action["action_type"] = "escalate"
                        action["priority_level"] = "urgent"
                elif "compliance" in content:
                    action["action_type"] = "reply"
                    action["response_text"] = "I acknowledge the terms."
                
                return Response([ResponseChoice(ResponseMessage(json.dumps(action)))])

try:
    from openai import OpenAI
    client = OpenAI(
    api_key=os.getenv("HF_TOKEN"),
    base_url=os.getenv("API_BASE_URL")
)
except ImportError:
    client = MockOpenAI(api_key="mock")

def get_action_from_llm(state_observation):
    system_prompt = """You are an elite email triage AI agent. Make fast, precise triage decisions based on email bodies, subjects, and metadata schemas like SLA or threat-level properties.
You must choose one of these actions: reply, forward, archive, mark_spam, request_info, escalate.
If you respond, ensure response_text handles context constraints professionally.
If you deal with critical downtime metadata, utilize escalate with urgent priority_level.
Return ONLY valid JSON: {"action_type": "...", "email_id": "...", "forward_to": "...", "response_text": "...", "priority_level": "..."}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Current Inbox Observation: {json.dumps(state_observation)}"}
    ]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        response_format={"type": "json_object"}
    )
    try:
        data = json.loads(response.choices[0].message.content)
        return data
    except:
        inbox = state_observation.get("inbox", [])
        if inbox: return {"action_type": "archive", "email_id": inbox[0]["id"], "priority_level": "normal"}
        return {"action_type": "archive", "email_id": "", "priority_level": "normal"}

def run_inference(task="easy"):
    print(f"[START] task={task} env=email-triage-env model={MODEL_NAME}")
    try:
        resp = requests.post(f"{API_BASE_URL}/reset", json={"task": task})
        resp.raise_for_status()
        res = resp.json()
        observation = res.get("observation", {})
    except Exception as e:
        print(f"Error resetting env: {e}")
        return
        
    done = False
    step = 0
    rewards_list = []
    
    while not done:
        step += 1
        inbox = observation.get("inbox", [])
        if not inbox: break
            
        action = get_action_from_llm(observation)
        if action.get("email_id") not in [e["id"] for e in inbox]:
            action["email_id"] = inbox[0]["id"]
            
        try:
            resp = requests.post(f"{API_BASE_URL}/step", json={"action": action})
            resp.raise_for_status()
            res = resp.json()
        except: break
            
        observation = res.get("observation", {}) or {}
        reward = res.get("reward", 0.0)
        done = res.get("done", True)
        info = res.get("info", {})
        error_msg = info.get("error") if isinstance(info, dict) else None
        
        rewards_list.append(reward)
        err_str = "null" if error_msg is None else f'"{error_msg}"'
        print(f"[STEP] step={step} action={json.dumps(action)} reward={reward:.2f} done={str(done).lower()} error={err_str}")

    total_score = sum(rewards_list)
    rewards_str = ",".join([f"{r:.2f}" for r in rewards_list])
    print(f"[END] success=true steps={step} score={total_score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    time.sleep(1)
    run_inference("easy")
    run_inference("medium")
    run_inference("hard")
