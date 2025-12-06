# adapt.py

from typing import Literal

Difficulty = Literal["easy", "medium", "hard"]


def choose_next_difficulty(current: Difficulty,
                           pronunciation_score: float,
                           focus_score: float) -> Difficulty:
    """
    Simple rule-based dynamic difficulty:
    - If both scores are high, increase difficulty.
    - If both are low, decrease difficulty.
    - Otherwise, keep same.
    """

    # thresholds can be tuned
    HIGH = 0.8
    LOW = 0.5

    if pronunciation_score >= HIGH and focus_score >= HIGH:
        if current == "easy":
            return "medium"
        if current == "medium":
            return "hard"
        return "hard"

    if pronunciation_score <= LOW or focus_score <= LOW:
        if current == "hard":
            return "medium"
        if current == "medium":
            return "easy"
        return "easy"

    return current
