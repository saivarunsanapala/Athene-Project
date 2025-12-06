# content.py

EASY_SENTENCES = [
    "The cat sat on the mat.",
    "I like red apples.",
    "The dog runs fast."
]

MEDIUM_SENTENCES = [
    "The little boy carefully crossed the busy street.",
    "Reading every day can slowly improve your skills.",
    "The teacher asked the students to repeat the sentence."
]

HARD_SENTENCES = [
    "She whispered the complicated instructions under her breath.",
    "Consistency and patience are essential for meaningful progress.",
    "The scientist meticulously documented the experimental procedure."
]


def get_sentences_by_level(level: str):
    level = level.lower()
    if level == "easy":
        return EASY_SENTENCES
    if level == "medium":
        return MEDIUM_SENTENCES
    if level == "hard":
        return HARD_SENTENCES
    return EASY_SENTENCES
