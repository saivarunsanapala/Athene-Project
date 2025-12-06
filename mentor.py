# mentor.py

from typing import Literal

Difficulty = Literal["easy", "medium", "hard"]


def generate_feedback(pron_score: float,
                      focus_score: float,
                      difficulty: Difficulty) -> str:
    """
    Rule-based mentor feedback message.
    """

    msgs = []

    # Pronunciation feedback
    if pron_score >= 0.85:
        msgs.append("Your pronunciation was very clear today. Great job!")
    elif pron_score >= 0.6:
        msgs.append("Your pronunciation is improving. Let's keep practicing the tricky words.")
    else:
        msgs.append("Some words were hard this time, but that's okay. We'll take it step by step.")

    # Focus feedback
    if focus_score >= 0.8:
        msgs.append("You stayed focused for most of the session. I'm proud of your effort!")
    elif focus_score >= 0.5:
        msgs.append("You were focused for part of the time. Let's try short breaks to help your attention.")
    else:
        msgs.append("It was hard to stay focused today. Maybe a shorter, fun session next time will help.")

    # Difficulty comment
    if difficulty == "easy":
        msgs.append("We'll keep the sentences simple until you feel more confident.")
    elif difficulty == "medium":
        msgs.append("You're ready for medium-level sentences now!")
    else:
        msgs.append("You're working on challenging sentences. That's a big step forward!")

    return " ".join(msgs)
