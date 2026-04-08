from typing import Dict, Any, Tuple
from .models import State, Action, Observation
from .tasks import get_initial_state
from .graders import grade_action

class EmailTriageEnv:
    def __init__(self):
        self._state: State = None
        self.current_task: str = "easy"

    async def reset(self, task: str = "easy") -> Tuple[Observation, Dict[str, Any]]:
        self.current_task = task
        self._state = get_initial_state(task)
        return self._state.observation, {}

    async def step(self, action_dict: dict) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        if self._state is None or self._state.is_done:
            obs = self._state.observation if self._state else None
            return obs, 0.0, True, {"error": "Environment must be reset before stepping"}
            
        try:
            action = Action(**action_dict)
        except Exception as e:
            self._state.step_count += 1
            if self._state.step_count >= self._state.max_steps:
                self._state.is_done = True
            return self._state.observation, 0.0, self._state.is_done, {"error": f"Invalid action format: {str(e)}"}
            
        self._state.step_count += 1
        
        email_to_process = None
        for i, email in enumerate(self._state.observation.inbox):
            if email.id == action.email_id:
                email_to_process = self._state.observation.inbox.pop(i)
                break
                
        if not email_to_process:
            self._state.is_done = len(self._state.observation.inbox) == 0 or self._state.step_count >= self._state.max_steps
            return self._state.observation, 0.0, self._state.is_done, {"error": "Email ID not found in inbox"}
            
        reward = grade_action(self.current_task, action, email_to_process, self._state)
        reward = max(0.0, min(1.0, reward))
        self._state.score = max(0.0, min(1.0, self._state.score + reward))
        
        if action.action_type == "reply":
            self._state.observation.replied.append(email_to_process)
        elif action.action_type == "forward":
            self._state.observation.forwarded.append(email_to_process)
        elif action.action_type == "archive":
            self._state.observation.archived.append(email_to_process)
        elif action.action_type == "mark_spam":
            self._state.observation.spam.append(email_to_process)
        elif action.action_type == "request_info":
            self._state.observation.pending_info.append(email_to_process)
        elif action.action_type == "escalate":
            self._state.observation.escalated.append(email_to_process)

        if len(self._state.observation.inbox) == 0 or self._state.step_count >= self._state.max_steps:
            self._state.is_done = True
            
        return self._state.observation, reward, self._state.is_done, {}

    def state(self) -> State:
        if self._state is None:
            self._state = get_initial_state("easy")
        return self._state
