# Smart AC Control System

A Python application that uses computer vision to detect people in a room and automatically control an AC system.

## Features

- 🎥 **Real-time person detection** using your laptop's camera
- 🔄 **Automatic AC control** - turns on when person detected, off after timeout
- ⏰ **Configurable timeout** - set how long to wait before turning off AC
- 📊 **Visual feedback** - see detection status and AC state on camera feed
- 📝 **Logging** - track all AC control events

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure your camera is working:**
   - Test your camera with any camera app
   - Make sure no other applications are using the camera

## Usage

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Configuration:**
   - The system will turn off AC after 5 minutes of no person detection (configurable)
   - Detection confidence threshold is set to 0.5 (configurable)
   - Press 'q' to quit the application

3. **What you'll see:**
   - Camera feed window showing detection status
   - Green "PERSON DETECTED" when someone is in frame
   - Red "NO PERSON" when no one is detected
   - AC status indicator
   - Timeout countdown when no person detected

## Configuration

You can modify these settings in `main.py`:

```python
timeout_minutes = 5  # Minutes to wait before turning off AC
confidence_threshold = 0.5  # Detection sensitivity (0.0-1.0)
```

## AC Control Integration

The current implementation includes a simulated AC control function. To integrate with real hardware:

1. **IR Blaster Control:**
   ```python
   # Example for IR control
   import serial
   
   def control_ac_ir(turn_on):
       ser = serial.Serial('COM3', 9600)  # Adjust port
       if turn_on:
           ser.write(b'AC_ON_COMMAND')
       else:
           ser.write(b'AC_OFF_COMMAND')
       ser.close()
   ```

2. **Smart Home Integration:**
   ```python
   # Example for Home Assistant
   import requests
   
   def control_ac_smart_home(turn_on):
       url = "http://homeassistant:8123/api/services/switch/turn_on"
       data = {"entity_id": "switch.ac_unit"}
       requests.post(url, json=data)
   ```

3. **WiFi AC Controller:**
   ```python
   # Example for WiFi AC controller
   import socket
   
   def control_ac_wifi(turn_on):
       # Send commands to your WiFi AC controller
       pass
   ```

## Troubleshooting

- **Camera not working:** Ensure no other apps are using the camera
- **Poor detection:** Adjust `confidence_threshold` (lower = more sensitive)
- **False positives:** Increase `confidence_threshold` (higher = less sensitive)
- **AC not responding:** Check your AC control integration code

## System Requirements

- Python 3.7+
- Webcam/camera
- Windows/Linux/macOS
- OpenCV and MediaPipe compatible system

## Logs

The system creates an `ac_control.log` file to track:
- AC on/off events
- Detection status changes
- System errors
- Timestamps for all events




