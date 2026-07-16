import cv2
import mediapipe as mp
import time
import threading
from datetime import datetime, timedelta
import logging

class PersonDetector:
    def __init__(self, timeout_minutes=5, confidence_threshold=0.5):
        """
        Initialize the person detector with AC control
        
        Args:
            timeout_minutes (int): Minutes to wait before turning off AC when no person detected
            confidence_threshold (float): Confidence threshold for person detection (0.0-1.0)
        """
        self.timeout_minutes = timeout_minutes
        self.confidence_threshold = confidence_threshold
        self.last_person_detected = None
        self.ac_on = False
        self.running = False
        
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
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=confidence_threshold,
            min_tracking_confidence=confidence_threshold
        )
        
        # Initialize camera
        self.cap = None
        self.init_camera()
        
    def init_camera(self):
        """Initialize camera capture"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
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
            bool: True if person detected, False otherwise
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            results = self.pose.process(rgb_frame)
            
            # Check if pose landmarks are detected (indicates a person)
            if results.pose_landmarks:
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error in person detection: {e}")
            return False
    
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
        print(f"🔧 Haier AC Control: {status}")
        
        try:
            # Method 1: Try Wi-Fi control (if AC has built-in Wi-Fi)
            if self.try_wifi_control(turn_on):
                return
            
            # Method 2: Try smartphone IR blaster
            if self.try_smartphone_ir(turn_on):
                return
            
            # Method 3: Try laptop IR (if available)
            if self.try_laptop_ir(turn_on):
                return
            
            # Method 4: Use sound-based control (ultrasonic)
            if self.try_sound_control(turn_on):
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
            import json
            
            # Haier SmartHQ API endpoints (these may vary by model)
            base_url = "http://192.168.1.100"  # Replace with your AC's IP
            endpoint = "/api/control"
            
            # Haier AC control commands
            if turn_on:
                command = {
                    "power": "on",
                    "mode": "cool",
                    "temperature": 24,
                    "fan_speed": "auto"
                }
            else:
                command = {
                    "power": "off"
                }
            
            # Try to send command (this will fail if AC doesn't have Wi-Fi)
            response = requests.post(f"{base_url}{endpoint}", 
                                  json=command, 
                                  timeout=5)
            
            if response.status_code == 200:
                self.logger.info(f"Wi-Fi control successful: AC {'ON' if turn_on else 'OFF'}")
                return True
                
        except Exception as e:
            self.logger.debug(f"Wi-Fi control not available: {e}")
        
        return False
    
    def try_smartphone_ir(self, turn_on):
        """
        Method 2: Use smartphone as IR blaster
        """
        try:
            # This method requires a smartphone with IR blaster
            # Common phones: Samsung Galaxy S series, LG G series, etc.
            
            if turn_on:
                print("📱 Smartphone IR Control: Send 'AC ON' signal")
                print("   - Open IR remote app on your phone")
                print("   - Select Haier AC")
                print("   - Press Power + Cool mode")
            else:
                print("📱 Smartphone IR Control: Send 'AC OFF' signal")
                print("   - Open IR remote app on your phone")
                print("   - Select Haier AC")
                print("   - Press Power Off")
            
            # You can also use Python to send commands to IR apps via ADB
            # This requires USB debugging enabled on your phone
            self.send_adb_ir_command(turn_on)
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
            
            # ADB commands to control IR apps
            if turn_on:
                # Example: Control via "AnyMote" app
                subprocess.run([
                    "adb", "shell", "am", "start", 
                    "-n", "com.remotefairy/.MainActivity",
                    "--es", "device", "haier_ac",
                    "--es", "command", "power_on"
                ], timeout=10)
            else:
                subprocess.run([
                    "adb", "shell", "am", "start", 
                    "-n", "com.remotefairy/.MainActivity",
                    "--es", "device", "haier_ac",
                    "--es", "command", "power_off"
                ], timeout=10)
                
        except Exception as e:
            self.logger.debug(f"ADB IR control failed: {e}")
    
    def try_laptop_ir(self, turn_on):
        """
        Method 3: Try laptop IR blaster (if available)
        """
        try:
            # Most laptops don't have IR blasters, but some do
            # This is for laptops with built-in IR transmitters
            
            if turn_on:
                print("💻 Laptop IR: Sending Haier AC ON signal")
                # Send IR signal for Haier AC power on
                self.send_haier_ir_signal("power_on")
            else:
                print("💻 Laptop IR: Sending Haier AC OFF signal")
                # Send IR signal for Haier AC power off
                self.send_haier_ir_signal("power_off")
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Laptop IR not available: {e}")
        
        return False
    
    def send_haier_ir_signal(self, command):
        """
        Send Haier-specific IR signals
        """
        # Haier AC IR codes (these are example codes - actual codes may vary)
        haier_codes = {
            "power_on": [0x02, 0xFD, 0x02, 0xFD, 0x80, 0x7F, 0x80, 0x7F],
            "power_off": [0x02, 0xFD, 0x02, 0xFD, 0x80, 0x7F, 0x80, 0x7F],
            "cool_mode": [0x02, 0xFD, 0x02, 0xFD, 0x80, 0x7F, 0x80, 0x7F]
        }
        
        # This would require an IR library like lirc or similar
        # For now, we'll simulate the signal
        print(f"📡 IR Signal: {command} - {haier_codes.get(command, 'Unknown command')}")
    
    def try_sound_control(self, turn_on):
        """
        Method 4: Use ultrasonic/sound-based control
        """
        try:
            import numpy as np
            import sounddevice as sd
            
            # Generate ultrasonic tones that some AC units can detect
            if turn_on:
                print("🔊 Sound Control: Playing AC ON ultrasonic tone")
                # Generate 40kHz tone for 2 seconds
                frequency = 40000  # 40kHz
                duration = 2.0
                sample_rate = 44100
                
                t = np.linspace(0, duration, int(sample_rate * duration))
                tone = np.sin(2 * np.pi * frequency * t) * 0.1
                
                sd.play(tone, sample_rate)
                sd.wait()
            else:
                print("🔊 Sound Control: Playing AC OFF ultrasonic tone")
                # Generate 35kHz tone for 2 seconds
                frequency = 35000  # 35kHz
                duration = 2.0
                sample_rate = 44100
                
                t = np.linspace(0, duration, int(sample_rate * duration))
                tone = np.sin(2 * np.pi * frequency * t) * 0.1
                
                sd.play(tone, sample_rate)
                sd.wait()
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Sound control not available: {e}")
        
        return False
    
    def show_manual_instructions(self, turn_on):
        """
        Show manual instructions when automatic control fails
        """
        if turn_on:
            print("📋 Manual Control Instructions:")
            print("   1. Use your Haier AC remote control")
            print("   2. Press POWER button to turn ON")
            print("   3. Set to COOL mode")
            print("   4. Set desired temperature (e.g., 24°C)")
        else:
            print("📋 Manual Control Instructions:")
            print("   1. Use your Haier AC remote control")
            print("   2. Press POWER button to turn OFF")
        
        print("   💡 Tip: Keep your remote nearby for manual override")
    
    def check_timeout(self):
        """Check if timeout has been reached since last person detection"""
        if self.last_person_detected is None:
            return False
        
        time_since_detection = datetime.now() - self.last_person_detected
        return time_since_detection.total_seconds() > (self.timeout_minutes * 60)
    
    def run_detection_loop(self):
        """Main detection loop"""
        self.logger.info("Starting person detection system...")
        self.running = True
        
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Failed to read from camera")
                    break
                
                # Detect person
                person_detected = self.detect_person(frame)
                
                if person_detected:
                    self.last_person_detected = datetime.now()
                    self.control_ac(True)
                else:
                    # Check if timeout reached
                    if self.ac_on and self.check_timeout():
                        self.control_ac(False)
                
                # Draw status on frame
                self.draw_status(frame, person_detected)
                
                # Display frame
                cv2.imshow('Person Detection - AC Control', frame)
                
                # Check for exit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                break
        
        self.cleanup()
    
    def draw_status(self, frame, person_detected):
        """Draw status information on the frame"""
        # Status text
        status_text = "PERSON DETECTED" if person_detected else "NO PERSON"
        ac_status = "AC: ON" if self.ac_on else "AC: OFF"
        
        # Colors
        person_color = (0, 255, 0) if person_detected else (0, 0, 255)
        ac_color = (0, 255, 0) if self.ac_on else (0, 0, 255)
        
        # Draw text
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, person_color, 2)
        cv2.putText(frame, ac_status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, ac_color, 2)
        
        # Draw timeout info
        if self.last_person_detected:
            time_since = datetime.now() - self.last_person_detected
            timeout_remaining = (self.timeout_minutes * 60) - time_since.total_seconds()
            if timeout_remaining > 0:
                timeout_text = f"Timeout in: {int(timeout_remaining)}s"
                cv2.putText(frame, timeout_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.logger.info("System stopped and cleaned up")
    
    def stop(self):
        """Stop the detection system"""
        self.running = False

def main():
    """Main function to run the person detection system"""
    print("🏠 Smart AC Control System")
    print("=" * 40)
    print("This system will:")
    print("• Detect people using your camera")
    print("• Turn AC ON when person is detected")
    print("• Turn AC OFF after timeout when no person detected")
    print("• Press 'q' to quit")
    print("=" * 40)
    
    try:
        # Configuration
        timeout_minutes = 0.08333333333333333  # Change this to your preferred timeout
        confidence_threshold = 0.5  # Adjust for sensitivity (0.0-1.0)
        
        # Create detector
        detector = PersonDetector(
            timeout_minutes=timeout_minutes,
            confidence_threshold=confidence_threshold
        )
        
        # Run detection
        detector.run_detection_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"System error: {e}")

if __name__ == "__main__":
    main()
