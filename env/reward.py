def compute_dense_reward(correct_action: bool) -> float:
    return 1.0 if correct_action else 0.0
