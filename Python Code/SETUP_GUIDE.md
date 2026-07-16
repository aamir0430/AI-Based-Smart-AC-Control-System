# 🏠 Complete Setup Guide - Haier AC Control System

## 📋 **Prerequisites**

### **System Requirements:**
- Windows 10/11 (you're already on this ✅)
- Python 3.7 or higher
- Webcam/camera (built-in or external)
- Internet connection for initial setup

### **Optional (for better control):**
- Smartphone with IR blaster (Samsung Galaxy S series, LG G series, etc.)
- Haier AC with Wi-Fi capability

---

## 🚀 **Step 1: Install Python**

### **Check if Python is already installed:**
1. Open **Command Prompt** (Press `Win + R`, type `cmd`, press Enter)
2. Type: `python --version`
3. If you see a version number (like Python 3.9.0), you're good to go!
4. If not, continue to install Python:

### **Install Python:**
1. Go to: https://www.python.org/downloads/
2. Download **Python 3.11** (latest stable version)
3. **IMPORTANT**: During installation, check ✅ **"Add Python to PATH"**
4. Click "Install Now"
5. Wait for installation to complete

### **Verify Python installation:**
```bash
python --version
pip --version
```

---

## 📁 **Step 2: Navigate to Your Project**

### **Open Command Prompt:**
1. Press `Win + R`
2. Type `cmd` and press Enter
3. Navigate to your project folder:

```bash
cd "C:\Users\skaam_nlyf2jt\OneDrive\Desktop\Project AC\Python Code"
```

### **Verify you're in the right folder:**
```bash
dir
```
You should see: `main.py`, `requirements.txt`, `README.md`

---

## 📦 **Step 3: Install Required Libraries**

### **Install all dependencies:**
```bash
pip install -r requirements.txt
```

### **If you get permission errors, try:**
```bash
pip install --user -r requirements.txt
```

### **If pip is not found, try:**
```bash
python -m pip install -r requirements.txt
```

### **Expected output:**
```
Collecting opencv-python==4.8.1.78
  Downloading opencv_python-4.8.1.78-cp311-cp311-win_amd64.whl
Collecting mediapipe==0.10.7
  Downloading mediapipe-0.10.7-cp311-cp311-win_amd64.whl
...
Successfully installed opencv-python-4.8.1.78 mediapipe-0.10.7 numpy-1.24.3 requests-2.31.0 sounddevice-0.4.6
```

---

## 🎥 **Step 4: Test Your Camera**

### **Before running the main program, test your camera:**

1. **Open Camera app** (search "Camera" in Start menu)
2. **Verify camera works** - you should see yourself
3. **Close Camera app** (important - only one app can use camera at a time)

### **If camera doesn't work:**
- Check if another app is using the camera
- Restart your laptop
- Update camera drivers

---

## 🏃‍♂️ **Step 5: Run the Program**

### **Start the AC control system:**
```bash
python main.py
```

### **What you should see:**
```
🏠 Smart AC Control System
========================================
This system will:
• Detect people using your camera
• Turn AC ON when person is detected
• Turn AC OFF after timeout when no person detected
• Press 'q' to quit
========================================
Camera initialized successfully
Starting person detection system...
```

### **A camera window will open showing:**
- Live camera feed
- "PERSON DETECTED" (green) or "NO PERSON" (red)
- "AC: ON" or "AC: OFF" status
- Timeout countdown when no person detected

---

## ⚙️ **Step 6: Configure for Your Haier AC**

### **Method 1: Wi-Fi Control (Best Option)**
If your Haier AC has Wi-Fi:

1. **Find your AC's IP address:**
   - Check your router's admin panel
   - Look for "Haier" device in connected devices
   - Or use: `ipconfig` in Command Prompt

2. **Edit the code:**
   - Open `main.py` in a text editor
   - Find line 154: `base_url = "http://192.168.1.100"`
   - Replace with your AC's actual IP address
   - Save the file

### **Method 2: Smartphone IR Control**
If you have a phone with IR blaster:

1. **Install IR remote app:**
   - Download "Remote Control for Haier AC" from Play Store
   - Or "AnyMote" app

2. **Enable USB debugging:**
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times
   - Go to Settings > Developer Options
   - Enable "USB Debugging"

3. **Connect phone to laptop:**
   - Use USB cable
   - Allow USB debugging when prompted

### **Method 3: Manual Control (Fallback)**
If automatic control doesn't work:
- Keep your Haier remote nearby
- The system will show instructions when needed
- You can manually control AC when prompted

---

## 🎯 **Step 7: Test the System**

### **Test person detection:**
1. **Stand in front of camera** - should show "PERSON DETECTED"
2. **Move away from camera** - should show "NO PERSON"
3. **Wait 5 minutes** - AC should turn off automatically

### **Test AC control:**
1. **When person detected** - check if AC turns on
2. **When no person for 5 minutes** - check if AC turns off
3. **Check the console output** for control method used

---

## 🔧 **Troubleshooting**

### **Camera Issues:**
```bash
# If camera doesn't work:
# 1. Close all other camera apps
# 2. Restart the program
# 3. Check camera permissions
```

### **Python Issues:**
```bash
# If "python" command not found:
py main.py

# If "pip" command not found:
python -m pip install -r requirements.txt
```

### **Library Issues:**
```bash
# If installation fails:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **AC Control Issues:**
- **Wi-Fi method**: Check AC's IP address
- **Smartphone IR**: Ensure USB debugging enabled
- **Manual control**: Keep remote nearby

---

## 📊 **Monitoring and Logs**

### **View system logs:**
- Open `ac_control.log` file
- See all AC control events
- Check for errors

### **Console output shows:**
- Detection status
- AC control attempts
- Which method worked
- Manual instructions if needed

---

## 🎮 **Controls**

### **Keyboard shortcuts:**
- **Press 'q'** - Quit the program
- **Press 'Esc'** - Quit the program
- **Close window** - Quit the program

### **Program will automatically:**
- Turn AC ON when person detected
- Turn AC OFF after 5 minutes of no person
- Show manual instructions if automatic control fails

---

## 🔄 **Daily Usage**

### **Starting the system:**
1. Open Command Prompt
2. Navigate to project folder
3. Run: `python main.py`
4. Position yourself in front of camera
5. Let the system work automatically

### **Stopping the system:**
- Press 'q' in the camera window
- Or close the camera window
- Or press Ctrl+C in Command Prompt

---

## 🆘 **Need Help?**

### **Common issues:**
1. **"Camera not found"** - Close other camera apps
2. **"Module not found"** - Reinstall requirements.txt
3. **"Permission denied"** - Run Command Prompt as Administrator
4. **"AC not responding"** - Check control method configuration

### **Getting support:**
- Check the console output for error messages
- Look at `ac_control.log` for detailed logs
- Ensure all prerequisites are met
- Try different control methods

---

## 🎉 **Success!**

Once everything is working:
- ✅ Camera detects people automatically
- ✅ AC turns on when person detected
- ✅ AC turns off after timeout
- ✅ System runs continuously
- ✅ Logs all activities

**Your smart AC control system is now ready!** 🏠❄️




