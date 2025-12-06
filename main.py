# main.py

from content import get_sentences_by_level
from listen import transcribe_audio, compare_texts, compute_pronunciation_score
from assist_layer import speak_text, render_annotated_sentence
from adapt import choose_next_difficulty
from mentor import generate_feedback


def run_session():
    print("=== AI Reading Assistant Demo ===")
    current_difficulty = "easy"
    sentences = get_sentences_by_level(current_difficulty)
    sentence_index = 0

    while True:
        if sentence_index >= len(sentences):
            sentence_index = 0  # loop

        target_sentence = sentences[sentence_index]
        print(f"\nCurrent difficulty: {current_difficulty}")
        print(f"Sentence to read:\n  \"{target_sentence}\"\n")

        # Step 1: Play TTS version
        play_tts = input("Play TTS for this sentence? (y/n): ").strip().lower()
        if play_tts == "y":
            speak_text(target_sentence)

        # Step 2: User records audio externally
        audio_path = input("Enter the path to your recorded audio file (.wav/.mp3), or 'q' to quit: ").strip()
        if audio_path.lower() == "q":
            break

        # Step 3: ASR
        asr_text = transcribe_audio(audio_path)
        if not asr_text:
            print("No transcription. You can manually type what you said.")
            asr_text = input("Type the sentence you spoke: ").strip()

        print(f"\nASR / Spoken text:\n  \"{asr_text}\"\n")

        # Step 4: Compare
        annotated = compare_texts(target_sentence, asr_text)
        pron_score = compute_pronunciation_score(annotated)

        print("Word-level feedback (colors in compatible terminals):")
        print(render_annotated_sentence(annotated))
        print(f"\nPronunciation score: {pron_score:.2f}")

        # Step 5: Focus score (for now, user input; later: from Observe module)
        focus_str = input("Approximate your focus score this session (0 to 1, e.g., 0.7): ").strip()
        try:
            focus_score = float(focus_str)
        except ValueError:
            focus_score = 0.7
            print("Invalid input. Using default focus score = 0.7")

        # Step 6: Difficulty adaptation
        next_diff = choose_next_difficulty(current_difficulty, pron_score, focus_score)
        print(f"\nSuggested next difficulty level: {next_diff}")

        # Step 7: Mentor feedback
        feedback = generate_feedback(pron_score, focus_score, next_diff)
        print("\nMentor says:")
        print(feedback)

        # Update state and move on
        current_difficulty = next_diff
        sentences = get_sentences_by_level(current_difficulty)
        sentence_index += 1

        cont = input("\nDo you want to try another sentence? (y/n): ").strip().lower()
        if cont != "y":
            break


if __name__ == "__main__":
    run_session()
