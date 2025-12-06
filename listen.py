# listen.py

from difflib import SequenceMatcher
from typing import List, Tuple

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


def transcribe_audio(audio_path: str) -> str:
    """
    Use Whisper (if installed) to transcribe an audio file to text.
    If Whisper is not available, returns an empty string.
    """
    if not WHISPER_AVAILABLE:
        print("[WARN] Whisper not installed. Returning empty transcript.")
        return ""

    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="en")
    text = result.get("text", "").strip()
    return text


def compare_texts(target: str, spoken: str) -> List[Tuple[str, str]]:
    """
    Compare target text with spoken text.
    Returns a list of (word, status) where status is:
    'correct', 'mispronounced', 'extra', or 'missing'.
    """
    target_words = target.lower().strip().split()
    spoken_words = spoken.lower().strip().split()

    sm = SequenceMatcher(a=target_words, b=spoken_words)
    annotated = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for w in target_words[i1:i2]:
                annotated.append((w, "correct"))
        elif tag == "replace":
            # target words mispronounced or replaced by spoken words
            for w in target_words[i1:i2]:
                annotated.append((w, "mispronounced"))
            for w in spoken_words[j1:j2]:
                annotated.append((w, "extra"))
        elif tag == "delete":
            # target words missing in spoken
            for w in target_words[i1:i2]:
                annotated.append((w, "missing"))
        elif tag == "insert":
            # extra words spoken
            for w in spoken_words[j1:j2]:
                annotated.append((w, "extra"))

    return annotated


def compute_pronunciation_score(annotated_words: List[Tuple[str, str]]) -> float:
    """
    Simple score = fraction of words that are 'correct'.
    """
    if not annotated_words:
        return 0.0
    correct = sum(1 for _, status in annotated_words if status == "correct")
    return correct / len(annotated_words)
