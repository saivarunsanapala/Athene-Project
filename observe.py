# observe.py

import cv2
import time
import numpy as np

try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False


class AttentionTracker:
    """
    Simple webcam-based attention tracker.
    'Focused' if a face is detected, 'distracted' otherwise.
    """

    def __init__(self):
        if not MP_AVAILABLE:
            raise ImportError("mediapipe is not installed.")
        self.mp_face_detection = mp.solutions.face_detection
        self.detector = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
        self.focus_history = []  # list of 1 (focused) or 0 (not focused)

    def run(self, duration_sec: int = 30):
        cap = cv2.VideoCapture(0)
        start_time = time.time()

        while cap.isOpened() and (time.time() - start_time) < duration_sec:
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.process(rgb_frame)

            if results.detections:
                focus_flag = 1
                status_text = "FOCUSED"
                color = (0, 255, 0)
            else:
                focus_flag = 0
                status_text = "DISTRACTED"
                color = (0, 0, 255)

            self.focus_history.append(focus_flag)
            cv2.putText(frame, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.imshow("Attention Tracker", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def get_focus_score(self) -> float:
        if not self.focus_history:
            return 0.0
        return float(np.mean(self.focus_history))


if __name__ == "__main__":
    if not MP_AVAILABLE:
        print("Install mediapipe to run attention tracking.")
    else:
        tracker = AttentionTracker()
        print("Starting attention tracker for 20 seconds. Press 'q' to stop early.")
        tracker.run(duration_sec=20)
        print("Focus score:", tracker.get_focus_score())
