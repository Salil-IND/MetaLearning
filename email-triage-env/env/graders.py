from .models import Action, Email, State
from .reward import compute_dense_reward

def grade_easy(action: Action, email: Email) -> float:
    if email.id == "e1":
        if action.action_type == "reply":
            return compute_dense_reward(True)
        return compute_dense_reward(False)
    if email.id == "e2":
        if action.action_type == "mark_spam":
            return compute_dense_reward(True)
        return compute_dense_reward(False)
    return compute_dense_reward(False)

def grade_medium(action: Action, email: Email) -> float:
    if email.id == "m1":
        # Missing order ID logic -> should request info
        if action.action_type == "request_info":
            return compute_dense_reward(True)
        elif action.action_type == "reply" and action.response_text:
            if "order" in action.response_text.lower() and "id" in action.response_text.lower():
                return compute_dense_reward(True)
            return compute_dense_reward(True) * 0.5
        elif action.action_type == "forward" and action.forward_to and "support" in action.forward_to.lower():
            # Escalating an incomplete ticket rather than asking for info gets partial score
            return compute_dense_reward(True) * 0.3
        return compute_dense_reward(False)
    elif email.id == "m2":
        if action.action_type in ["mark_spam", "archive"]:
            return compute_dense_reward(True)
        return compute_dense_reward(False)
    elif email.id == "m3":
        if action.action_type == "reply" and action.response_text and len(action.response_text) > 5:
            return compute_dense_reward(True)
        elif action.action_type == "reply":
            return compute_dense_reward(True) * 0.5
        return compute_dense_reward(False)
    return compute_dense_reward(False)

def grade_hard(action: Action, email: Email) -> float:
    if email.id == "h1": # VIP Issue
        # We need reply containing "investigating" or "downtime"
        base = 0.0
        if action.action_type == "reply":
            if action.response_text and "investigat" in action.response_text.lower():
                base = 1.0
            else:
                base = 0.5
        elif action.action_type == "escalate":
            if action.priority_level == "urgent":
                base = 1.0
            else:
                base = 0.7
        return compute_dense_reward(True) * base
        
    elif email.id == "h2": # Alert
        if action.action_type == "escalate":
            if action.priority_level == "urgent":
                return compute_dense_reward(True)
            return compute_dense_reward(True) * 0.7
        elif action.action_type == "forward" and action.forward_to and "eng" in action.forward_to.lower():
            if action.priority_level == "urgent":
                return compute_dense_reward(True)
            return compute_dense_reward(True) * 0.5
        return compute_dense_reward(False)
        
    elif email.id == "h3": # Compliance
        if action.action_type == "reply":
            if action.response_text and "acknowledge" in action.response_text.lower():
                return compute_dense_reward(True)
            return compute_dense_reward(True) * 0.4
        elif action.action_type == "forward" and action.forward_to and "legal" in action.forward_to.lower():
            return compute_dense_reward(True)
        return compute_dense_reward(False)
        
    elif email.id == "h4": # CEO Phish Attack
        if action.action_type == "mark_spam":
            return compute_dense_reward(True)
        elif action.action_type == "archive" or action.action_type == "escalate":
            return compute_dense_reward(True) * 0.5
        return compute_dense_reward(False)
        
    elif email.id == "h5": # Intern project
        if action.action_type == "reply":
            return compute_dense_reward(True)
        return compute_dense_reward(False)

    return compute_dense_reward(False)

def grade_action(task_level: str, action: Action, email: Email, state: State) -> float:
    tasks_sizes = {"easy": 2, "medium": 3, "hard": 5}
    size = tasks_sizes.get(task_level, 1)
    
    if task_level == "easy":
        r = grade_easy(action, email)
    elif task_level == "medium":
        r = grade_medium(action, email)
    elif task_level == "hard":
        r = grade_hard(action, email)
    else:
        r = 0.0
        
    # Strictly bound reward between 0.0 and 1.0 for this step
    # Max episode score stays bounded since pop removes 1 email, at max 1 for each email / sizes = 1.0 total max
    scaled_reward = max(0.0, min(1.0, r / size))
    return scaled_reward
