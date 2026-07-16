import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarksConnections
import time
import threading
from datetime import datetime, timedelta
import logging
import os
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TIMEOUT_SECONDS = 5          # Seconds with no person before AC turns off (use 300 for 5 min)
CONFIDENCE_THRESHOLD = 0.5   # Person detection sensitivity (0.0-1.0)
AC_WIFI_IP = "http://192.168.1.100"  # Set your Haier AC IP for automatic Wi-Fi control
MODEL_PATH = os.path.join("models", "pose_landmarker_lite.task")
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)


def ensure_pose_model(model_path=MODEL_PATH, model_url=MODEL_URL):
    """Download the pose landmarker model if it is not already present."""
    if os.path.exists(model_path):
        return model_path

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    print("Downloading pose detection model (one-time setup)...")
    urllib.request.urlretrieve(model_url, model_path)
    print(f"Model saved to {model_path}")
    return model_path


class PersonDetector:
    def __init__(self, timeout_seconds=TIMEOUT_SECONDS, confidence_threshold=CONFIDENCE_THRESHOLD):
        """
        Initialize the person detector with AC control

        Args:
            timeout_seconds (int): Seconds to wait before turning off AC when no person detected
            confidence_threshold (float): Confidence threshold for person detection (0.0-1.0)
        """
        self.timeout_seconds = timeout_seconds
        self.confidence_threshold = confidence_threshold
        self.last_person_detected = None
        self.ac_on = False
        self.running = False
        self.frame_timestamp_ms = 0

        # Setup logging EARLY (must exist before any method uses self.logger)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ac_control.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Initialize MediaPipe Pose Landmarker (Tasks API for mediapipe >= 0.10.14)
        model_path = ensure_pose_model()
        options = vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=confidence_threshold,
            min_pose_presence_confidence=confidence_threshold,
            min_tracking_confidence=confidence_threshold,
        )
        self.pose_landmarker = vision.PoseLandmarker.create_from_options(options)
        self.pose_connections = PoseLandmarksConnections.POSE_LANDMARKS

        # Initialize camera
        self.cap = None
        self.init_camera()

    def init_camera(self):
        """Initialize camera capture"""
        try:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                raise Exception("Could not open camera")

            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            # Warm up camera — first frames are often empty on Windows
            for _ in range(15):
                self.cap.read()
                time.sleep(0.03)

            self.logger.info("Camera initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            raise

    def detect_person(self, frame):
        """
        Detect if there's a person in the frame

        Args:
            frame: OpenCV frame

        Returns:
            tuple: (person_detected: bool, pose_landmarks or None)
        """
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = self.pose_landmarker.detect_for_video(mp_image, self.frame_timestamp_ms)
            self.frame_timestamp_ms += 33

            if results.pose_landmarks:
                return True, results.pose_landmarks[0]
            return False, None

        except Exception as e:
            self.logger.error(f"Error in person detection: {e}")
            return False, None

    def control_ac(self, turn_on):
        """
        Control the Haier AC system

        Args:
            turn_on (bool): True to turn on AC, False to turn off
        """
        try:
            if turn_on and not self.ac_on:
                self.ac_on = True
                self.logger.info("Haier AC TURNED ON - Person detected")
                self.control_haier_ac(True)

            elif not turn_on and self.ac_on:
                self.ac_on = False
                self.logger.info("Haier AC TURNED OFF - No person detected for timeout period")
                self.control_haier_ac(False)

        except Exception as e:
            self.logger.error(f"Error controlling Haier AC: {e}")

    def control_haier_ac(self, turn_on):
        """
        Control Haier AC using multiple methods (no additional hardware required)
        """
        status = "ON" if turn_on else "OFF"
        print(f"Haier AC Control: {status}")

        try:
            # Method 1: Try Wi-Fi control (if AC has built-in Wi-Fi)
            if self.try_wifi_control(turn_on):
                return

            # Method 2: Try smartphone IR blaster via ADB
            if self.try_smartphone_ir(turn_on):
                return

            # Method 3: Try laptop IR (if available)
            if self.try_laptop_ir(turn_on):
                return

            # Fallback: Show instructions for manual control
            self.show_manual_instructions(turn_on)

        except Exception as e:
            self.logger.error(f"Error controlling Haier AC: {e}")
            self.show_manual_instructions(turn_on)

    def try_wifi_control(self, turn_on):
        """
        Method 1: Try to control via Wi-Fi (if AC has built-in Wi-Fi)
        """
        try:
            import requests

            base_url = AC_WIFI_IP
            endpoint = "/api/control"

            if turn_on:
                command = {
                    "power": "on",
                    "mode": "cool",
                    "temperature": 24,
                    "fan_speed": "auto"
                }
            else:
                command = {"power": "off"}

            response = requests.post(
                f"{base_url}{endpoint}",
                json=command,
                timeout=5
            )

            if response.status_code == 200:
                self.logger.info(f"Wi-Fi control successful: AC {'ON' if turn_on else 'OFF'}")
                return True

        except Exception as e:
            self.logger.debug(f"Wi-Fi control not available: {e}")

        return False

    def try_smartphone_ir(self, turn_on):
        """
        Method 2: Use smartphone as IR blaster via ADB
        """
        try:
            if self.send_adb_ir_command(turn_on):
                action = "ON" if turn_on else "OFF"
                self.logger.info(f"Smartphone IR control successful: AC {action}")
                return True

        except Exception as e:
            self.logger.debug(f"Smartphone IR control not available: {e}")

        return False

    def send_adb_ir_command(self, turn_on):
        """
        Send IR commands via ADB to smartphone
        """
        try:
            import subprocess

            command = "power_on" if turn_on else "power_off"
            result = subprocess.run(
                [
                    "adb", "shell", "am", "start",
                    "-n", "com.remotefairy/.MainActivity",
                    "--es", "device", "haier_ac",
                    "--es", "command", command
                ],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0

        except Exception as e:
            self.logger.debug(f"ADB IR control failed: {e}")
            return False

    def try_laptop_ir(self, turn_on):
        """
        Method 3: Try laptop IR blaster (placeholder — most laptops lack IR)
        """
        return False

    def show_manual_instructions(self, turn_on):
        """
        Show manual instructions when automatic control fails
        """
        if turn_on:
            print("Manual Control Instructions:")
            print("   1. Use your Haier AC remote control")
            print("   2. Press POWER button to turn ON")
            print("   3. Set to COOL mode")
            print("   4. Set desired temperature (e.g., 24 C)")
        else:
            print("Manual Control Instructions:")
            print("   1. Use your Haier AC remote control")
            print("   2. Press POWER button to turn OFF")

        print("   Tip: Set AC_WIFI_IP in main.py for automatic Wi-Fi control")

    def check_timeout(self):
        """Check if timeout has been reached since last person detection"""
        if self.last_person_detected is None:
            return False

        time_since_detection = datetime.now() - self.last_person_detected
        return time_since_detection.total_seconds() > self.timeout_seconds

    def run_detection_loop(self):
        """Main detection loop"""
        self.logger.info("Starting person detection system...")
        self.running = True
        failed_reads = 0

        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    failed_reads += 1
                    if failed_reads >= 30:
                        self.logger.error("Failed to read from camera")
                        break
                    time.sleep(0.05)
                    continue

                failed_reads = 0

                person_detected, pose_landmarks = self.detect_person(frame)

                if person_detected:
                    self.last_person_detected = datetime.now()
                    self.control_ac(True)
                elif self.ac_on and self.check_timeout():
                    self.control_ac(False)

                self.draw_status(frame, person_detected, pose_landmarks)

                cv2.imshow('Person Detection - AC Control', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                break

        self.cleanup()

    def draw_status(self, frame, person_detected, pose_landmarks=None):
        """Draw status information on the frame"""
        if pose_landmarks is not None:
            mp_drawing.draw_landmarks(
                frame,
                pose_landmarks,
                self.pose_connections,
            )

        status_text = "PERSON DETECTED" if person_detected else "NO PERSON"
        ac_status = "AC: ON" if self.ac_on else "AC: OFF"

        person_color = (0, 255, 0) if person_detected else (0, 0, 255)
        ac_color = (0, 255, 0) if self.ac_on else (0, 0, 255)

        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, person_color, 2)
        cv2.putText(frame, ac_status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, ac_color, 2)

        if self.last_person_detected:
            time_since = datetime.now() - self.last_person_detected
            timeout_remaining = self.timeout_seconds - time_since.total_seconds()
            if timeout_remaining > 0:
                timeout_text = f"Timeout in: {int(timeout_remaining)}s"
                cv2.putText(frame, timeout_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        if hasattr(self, "pose_landmarker") and self.pose_landmarker:
            self.pose_landmarker.close()
            self.pose_landmarker = None
        cv2.destroyAllWindows()
        self.logger.info("System stopped and cleaned up")

    def stop(self):
        """Stop the detection system"""
        self.running = False


def main():
    """Main function to run the person detection system"""
    print("Smart AC Control System")
    print("=" * 40)
    print("This system will:")
    print("- Detect people using your camera")
    print("- Turn AC ON when person is detected")
    print("- Turn AC OFF after timeout when no person detected")
    print("- Press 'q' to quit")
    print("=" * 40)

    try:
        detector = PersonDetector(
            timeout_seconds=TIMEOUT_SECONDS,
            confidence_threshold=CONFIDENCE_THRESHOLD
        )
        detector.run_detection_loop()

    except KeyboardInterrupt:
        print("\nSystem stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"System error: {e}")


if __name__ == "__main__":
    main()
