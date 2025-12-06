import streamlit as st
from typing import List, Tuple, Literal
from io import BytesIO
from difflib import SequenceMatcher
import numpy as np

# ===== ASR (Whisper) setup =====
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# ===== Simple reading content by difficulty =====

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


def get_sentences_by_level(level: str) -> List[str]:
    level = level.lower()
    if level == "easy":
        return EASY_SENTENCES
    if level == "medium":
        return MEDIUM_SENTENCES
    if level == "hard":
        return HARD_SENTENCES
    return EASY_SENTENCES


# ===== Listen module: ASR + comparison =====

def load_whisper_model():
    """Load Whisper model once and cache it in Streamlit session_state."""
    if "whisper_model" not in st.session_state:
        st.session_state.whisper_model = whisper.load_model("base")
    return st.session_state.whisper_model


def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """
    Use Whisper (if installed) to transcribe raw audio bytes.
    Returns recognized text, or "" if ASR is unavailable.
    """
    if not WHISPER_AVAILABLE:
        return ""

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        model = load_whisper_model()
        result = model.transcribe(tmp.name, language="en")
        return result.get("text", "").strip()


def compare_texts(target: str, spoken: str) -> List[Tuple[str, str]]:
    """
    Compare target text with spoken text.
    Returns list of (word, status) with status in:
    'correct', 'mispronounced', 'extra', 'missing'.
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
            for w in target_words[i1:i2]:
                annotated.append((w, "mispronounced"))
            for w in spoken_words[j1:j2]:
                annotated.append((w, "extra"))
        elif tag == "delete":
            for w in target_words[i1:i2]:
                annotated.append((w, "missing"))
        elif tag == "insert":
            for w in spoken_words[j1:j2]:
                annotated.append((w, "extra"))

    return annotated


def compute_pronunciation_score(annotated_words: List[Tuple[str, str]]) -> float:
    """Pronunciation score = fraction of 'correct' words."""
    if not annotated_words:
        return 0.0
    correct = sum(1 for _, status in annotated_words if status == "correct")
    return correct / len(annotated_words)


# ===== Assist layer: TTS + visual highlighting =====

from gtts import gTTS


def synthesize_tts_bytes(text: str, lang: str = "en") -> bytes:
    """
    Use gTTS to synthesize speech and return as bytes.
    Streamlit will handle playback via st.audio().
    """
    fp = BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()


def render_annotated_html(annotated_words: List[Tuple[str, str]]) -> str:
    """
    Return HTML string where each word is color-coded:
      green: correct
      yellow: mispronounced
      red: missing
      blue: extra
    """
    COLORS = {
        "correct": "#a5d6a7",        # light green
        "mispronounced": "#fff59d",  # light yellow
        "missing": "#ef9a9a",        # light red
        "extra": "#90caf9",          # light blue
    }

    parts = []
    for word, status in annotated_words:
        color = COLORS.get(status, "#e0e0e0")
        parts.append(
            f'<span style="background-color:{color}; padding:2px 4px; '
            f'margin:2px; border-radius:4px; display:inline-block;">{word}</span>'
        )
    return " ".join(parts)


# ===== Adapt module =====

Difficulty = Literal["easy", "medium", "hard"]


def choose_next_difficulty(current: Difficulty,
                           pronunciation_score: float,
                           focus_score: float) -> Difficulty:
    """
    Simple rule-based adaptation:
    - If both scores are high → increase difficulty
    - If either is low → decrease difficulty
    - Otherwise → keep same
    """
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


# ===== Mentor persona =====

def generate_feedback(pron_score: float,
                      focus_score: float,
                      difficulty: Difficulty) -> str:
    msgs = []

    # Pronunciation
    if pron_score >= 0.85:
        msgs.append("Your pronunciation was very clear. Great job! ")
    elif pron_score >= 0.6:
        msgs.append("Your pronunciation is improving. Let's keep practicing the tricky words. ")
    else:
        msgs.append("Some words were difficult this time, but that's okay. We'll take it step by step. ")

    # Focus
    if focus_score >= 0.8:
        msgs.append("You stayed focused for most of the session. I'm proud of your effort! ")
    elif focus_score >= 0.5:
        msgs.append("You were focused for part of the time. Short breaks might help you stay engaged. ")
    else:
        msgs.append("It was hard to stay focused today. A shorter, fun session next time could help. ")

    # Difficulty
    if difficulty == "easy":
        msgs.append("We'll keep the sentences simple until you feel more confident.")
    elif difficulty == "medium":
        msgs.append("You're ready for medium-level sentences now!")
    else:
        msgs.append("You're working on challenging sentences. That's a big step forward!")

    return "".join(msgs)


# ===== Streamlit app logic =====

def init_session_state():
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "easy"
    if "sentence_index" not in st.session_state:
        st.session_state.sentence_index = 0
    if "last_pron_score" not in st.session_state:
        st.session_state.last_pron_score = None
    if "last_focus_score" not in st.session_state:
        st.session_state.last_focus_score = None
    if "last_spoken_text" not in st.session_state:
        st.session_state.last_spoken_text = ""
    if "last_annotated" not in st.session_state:
        st.session_state.last_annotated = []


def main():
    st.set_page_config(page_title="AI Reading Assistant", layout="wide")
    init_session_state()

    st.title("📖 AI Reading Assistant (Prototype)")

    # Sidebar: session info
    with st.sidebar:
        st.header("Session Info")
        st.write(f"**Current difficulty:** {st.session_state.difficulty.capitalize()}")
        st.write(f"**Sentence index:** {st.session_state.sentence_index + 1}")

        if st.session_state.last_pron_score is not None:
            st.metric("Last pronunciation score", f"{st.session_state.last_pron_score:.2f}")
        if st.session_state.last_focus_score is not None:
            st.metric("Last focus score", f"{st.session_state.last_focus_score:.2f}")

        if st.button("🔄 Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

    # Main layout
    col_left, col_right = st.columns([2, 1])

    # Get current sentence
    sentences = get_sentences_by_level(st.session_state.difficulty)
    idx = st.session_state.sentence_index % len(sentences)
    target_sentence = sentences[idx]

    with col_left:
        st.subheader("Step 1: Read the sentence")
        st.markdown(f"> **Target sentence:**  \n> {target_sentence}")

        # TTS playback
        if st.button("🔊 Play sentence (TTS)"):
            with st.spinner("Generating audio..."):
                audio_bytes = synthesize_tts_bytes(target_sentence)
            st.audio(audio_bytes, format="audio/mp3")

        st.markdown("---")
        st.subheader("Step 2: Upload your reading")

        uploaded_file = st.file_uploader(
            "Upload your recorded reading (wav/mp3/m4a/ogg etc.)",
            type=["wav", "mp3", "m4a", "ogg"]
        )

        use_manual_input = st.checkbox("I can't use ASR / Whisper. I'll type what I read instead.", value=not WHISPER_AVAILABLE)

        spoken_text = ""

        if uploaded_file is not None and not use_manual_input:
            if WHISPER_AVAILABLE:
                if st.button("🎙️ Analyze my reading"):
                    audio_bytes = uploaded_file.read()
                    with st.spinner("Running speech recognition..."):
                        spoken_text = transcribe_audio_bytes(audio_bytes)
                    st.session_state.last_spoken_text = spoken_text
                    st.success("Transcription complete!")
            else:
                st.info("Whisper is not installed. Check the box above to type your spoken sentence manually.")

        if use_manual_input:
            spoken_text = st.text_area(
                "Type the sentence you spoke (approximate is okay):",
                value=st.session_state.last_spoken_text,
                height=80
            )
            if st.button("📝 Analyze typed reading"):
                st.session_state.last_spoken_text = spoken_text

    with col_right:
        st.subheader("Step 3: Feedback & Adaptation")

        if st.session_state.last_spoken_text:
            spoken_text = st.session_state.last_spoken_text

            # Compare & score
            annotated = compare_texts(target_sentence, spoken_text)
            pron_score = compute_pronunciation_score(annotated)

            st.session_state.last_pron_score = pron_score
            st.session_state.last_annotated = annotated

            st.markdown("**Word-level feedback:**")
            html = render_annotated_html(annotated)
            st.markdown(html, unsafe_allow_html=True)

            st.write(f"**Pronunciation score:** `{pron_score:.2f}`")

            st.markdown("---")
            st.markdown("**Step 4: Attention / focus estimate**")
            focus_score = st.slider(
                "How focused did you feel while reading?",
                min_value=0.0, max_value=1.0, value=0.7, step=0.05,
                help="Later this can come from a webcam-based attention tracker."
            )
            st.session_state.last_focus_score = focus_score

            if st.button("📈 Get mentor feedback & next sentence"):
                # Adapt difficulty
                next_diff: Difficulty = choose_next_difficulty(
                    st.session_state.difficulty,
                    pron_score,
                    focus_score
                )
                feedback = generate_feedback(pron_score, focus_score, next_diff)

                st.success("Difficulty updated!")
                st.write(f"**Next difficulty level:** {next_diff.capitalize()}")

                st.markdown("**Mentor says:**")
                st.info(feedback)

                # Move to next sentence and difficulty
                st.session_state.difficulty = next_diff
                st.session_state.sentence_index += 1

                # Clear last spoken text for next round
                st.session_state.last_spoken_text = ""
                st.session_state.last_annotated = []

                st.experimental_rerun()

        else:
            st.info("Upload audio or type what you read, then click analyze to see feedback.")

    st.markdown("---")
    st.caption("Prototype for an AI-powered assistive reading tool with Listen, Adapt, Assist, and Mentor modules.")


if __name__ == "__main__":
    main()
