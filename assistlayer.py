# assist_layer.py

from typing import List, Tuple
from gtts import gTTS
import os
import pygame


def speak_text(text: str, lang: str = "en"):
    """
    Use gTTS + pygame to speak a sentence.
    """
    tts = gTTS(text=text, lang=lang)
    filename = "tts_output.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait until finished
    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.music.unload()
    pygame.mixer.quit()
    os.remove(filename)


def render_annotated_sentence(annotated_words: List[Tuple[str, str]]) -> str:
    """
    Create a color-marked string for console output.
    (Green = correct, Yellow = mispronounced, Red = missing, Blue = extra)

    Uses ANSI escape codes (works in many terminals).
    """
    COLOR = {
        "correct": "\033[92m",       # green
        "mispronounced": "\033[93m", # yellow
        "missing": "\033[91m",       # red
        "extra": "\033[94m",         # blue
    }
    RESET = "\033[0m"

    parts = []
    for word, status in annotated_words:
        color = COLOR.get(status, "")
        parts.append(f"{color}{word}{RESET}")

    return " ".join(parts)
