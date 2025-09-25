# RB2 Auto Download

Automated login and data download tool for RunningBall Trader Client application.

## Overview

This tool automates the process of logging into the RunningBall Trader Client, configuring timezone settings, and downloading data files. It uses GUI automation to interact with the application and OCR technology to recognize dates on the calendar interface.

## VM Specification Requirements

### Minimum System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum, 8 cores recommended
- **Storage**: 50GB free disk space
- **Display Resolution**: 1920x1080 minimum (Full HD)
- **Network**: Stable internet connection

### Display Configuration
- **Screen Resolution**: Must be set to **1920x1080**
- **Display Scaling**: 150%

> ⚠️ **Important**: The tool uses pixel-perfect coordinate detection. Display resolution and scaling settings must match the requirements for proper functionality.

## Deployment Instructions

### 1. System Prerequisites

#### Install Python 3.8+
```bash
# Download from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
```

#### Install Tesseract OCR
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR\
```

#### Install RunningBall Trader Client
```bash
# Install to default location:
# C:\Program Files (x86)\Runningball Sports Information\Runningball Trader Client\
```

### 2. Python Dependencies

Install required Python packages:
```bash
pip install pywinauto
pip install pyautogui
pip install pillow
pip install opencv-python
pip install numpy
pip install pytesseract
pip install pywin32
```

Or use requirements file:
```bash
pip install -r requirements.txt
```

### 3. Project Setup

1. Clone or download the project files
2. Ensure the following files are present:
   ```
   RB2-auto-download/
   ├── runningball_login.py
   ├── time_adjuster.py
   ├── display_spec.jpg
   └── README.md
   ```

3. Create output directory:
   ```bash
   mkdir C:\RB2
   ```

### 4. Configuration

#### Update Credentials (if needed)
If you need to change login credentials, modify the `get_credentials()` function in `runningball_login.py`:

```python
def get_credentials():
    username = "YOUR_USERNAME"
    # Encode your password to base64
    encrypted_password = "YOUR_BASE64_ENCODED_PASSWORD"
    # ...
```

To encode a new password:
```python
import base64
password = "your_new_password"
encoded = base64.b64encode(password.encode()).decode()
print(f"Encoded password: {encoded}")
```

## Workflow Process

### Main Workflow Steps

1. **Application Connection**
   - Terminates existing RunningBall processes
   - Launches RunningBall Trader Client
   - Maximizes window and brings to foreground

2. **Authentication**
   - Loads encrypted credentials
   - Fills username and password fields
   - Performs login

3. **Settings Configuration**
   - Navigates to settings (coordinates: 370, 60)
   - Configures timezone to "America/Puerto_Rico"
   - Saves settings

4. **Data Download Process**
   - Navigates to calendar view (coordinates: 200, 60)
   - Takes screenshot for OCR analysis
   - Recognizes available dates using Tesseract OCR
   - Iterates through each recognized date:
     - Clicks on date
     - Initiates download (coordinates: 60, 200)
     - Handles save dialog with auto-generated filename
     - Saves file as: `C:\RB2\RB2-{DD-MM-YYYY}sc.xls`

5. **Cleanup**
   - Removes temporary screenshot files
   - Reports completion status

### File Naming Convention

Downloaded files follow this pattern:
```
C:\RB2\RB2-{DD-MM-YYYY}sc.xls
```

Examples:
- `C:\RB2\RB2-25-09-2024sc.xls`
- `C:\RB2\RB2-26-09-2024sc.xls`

## Usage

### Basic Execution
```bash
python runningball_login.py
```

### Expected Output
```
🎯 RunningBall Login Tool
========================================
🚀 Connecting to RunningBall... (Attempt 1/3)
✅ Connected to existing application
✅ Found window: RunningBall Trader
📏 Maximizing window...
✅ Window maximized
🎯 Focusing to foreground...
✅ Focused to foreground

🔐 Loading credentials...
🔐 Starting login...
📝 Username: OW078
🔒 Password: **********
✅ Login operation completed

🖱️ Click coordinates (370, 60)...
✅ SettingClick completed
🕐 Start handling timezone settings...
✅ Timezone settings saved

🖱️ Click coordinates (200, 60)...
✅ CalendarClick completed
📅 Attempting to recognize dates and coordinates on screen...
🎯 Click 1 date: Tue, 24.09 (in date order)
✅ Download click completed
💾 Processing save dialog...
✅ Save completed: C:\RB2\RB2-24-09-2024sc.xls

🎉 Login process completed!
🧹 Starting screenshot cleanup...
```

## Troubleshooting

### Common Issues

#### 1. Application Not Found
```
❌ Unable to connect to application
```
**Solution**: Verify RunningBall is installed in the default location

#### 2. OCR Recognition Failed
```
❌ OCR recognition failed
```
**Solution**: 
- Check Tesseract installation path
- Verify display resolution settings
- Ensure calendar view is visible

#### 3. Coordinate Mismatch
```
❌ Click failed or unexpected behavior
```
**Solution**:
- Verify display resolution is 1920x1080
- Check display scaling is set to 100%
- Ensure window is maximized

#### 4. Save Dialog Issues
```
❌ Save handling failed
```
**Solution**:
- Ensure C:\RB2 directory exists
- Check file permissions
- Verify disk space availability

### Debug Mode

For debugging, you can modify the script to:
- Keep screenshot files (comment out `cleanup_screenshots()`)
- Add more logging output
- Adjust timing delays

## Security Notes

- Credentials are stored using base64 encoding (not plain text)
- No external configuration files required
- All credential handling is contained within the main script

## File Structure

```
C:\Dev\rb2-auto-download\
├── runningball_login.py    # Main automation script
├── time_adjuster.py        # Time adjustment utility
├── display_spec.jpg        # Display specification reference
├── README.md              # This documentation
└── requirements.txt       # Python dependencies (create if needed)

C:\RB2\                    # Output directory (created automatically)
├── RB2-DD-MM-YYYYsc.xls  # Downloaded data files
└── ...
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Ensure display settings match requirements
4. Review the console output for specific error messages

## Version History

- **v1.0**: Initial release with basic automation
- **v1.1**: Added password encryption and English localization
- **v1.2**: Simplified credential management