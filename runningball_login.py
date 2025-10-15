#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RunningBall Login Tool
1. Maximize window
2. Focus to foreground
3. Find "Username" text and fill in account in the input box on the right
4. Find "Password" text and fill in password in the input box on the right
"""

from pywinauto import Application
import pyautogui
import time
from PIL import ImageGrab
import cv2
import numpy as np
from datetime import datetime
import base64
from send_email_to_est import clear_all_files_in_rb2, send_email_to_est
def connect_and_maximize():
    
    """Connect to application and maximize, retry 3 times on failure"""
    app_path = r"C:\Program Files (x86)\Runningball Sports Information\Runningball Trader Client\RunningBall.exe"
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # First terminate existing RunningBall.exe processes
            kill_runningball_process()
            
            print(f"🚀 Connecting to RunningBall... (Attempt {attempt + 1}/{max_retries})")
            
            # Try to connect to existing application
            app = None
            try:
                app = Application(backend="uia").connect(path=app_path)
                print("✅ Connected to existing application")
            except:
                # Start new application
                print("📱 Starting new application...")
                try:
                    app = Application(backend="uia").start(app_path)
                    time.sleep(15)
                    print("✅ Application started")
                except Exception as start_error:
                    print(f"❌ Application startup failed: {start_error}")
                    if attempt < max_retries - 1:
                        print(f"⏰ Waiting 5 seconds before retry...")
                        time.sleep(5)
                        continue
                    else:
                        raise start_error
            
            if not app:
                raise Exception("Unable to get application object")
            
            # Find window
            print("🔍 Looking for window...")
            try:
                window = app.window(title_re=r".*RunningBall.*")
                window.wait("ready", timeout=10)
                
                window_title = window.window_text()
                print(f"✅ Found window: {window_title}")
            except Exception as window_error:
                print(f"❌ Window search failed: {window_error}")
                if attempt < max_retries - 1:
                    print(f"⏰ Wait 5 seconds before retry...")
                    time.sleep(5)
                    continue
                else:
                    raise window_error
            
            # Maximize window
            print("📏 Maximizing window...")
            try:
                import win32gui
                hwnd = window.handle
                win32gui.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
                time.sleep(1)
                print("✅ Window maximized")
            except:
                try:
                    window.maximize()
                    time.sleep(1)
                    print("✅ Window maximized")
                except Exception as max_error:
                    print(f"⚠️ Maximization failed: {max_error}")
            
            # Focus to foreground
            print("🎯 Focusing to foreground...")
            try:
                window.set_focus()
                time.sleep(1)
                
                # Force foreground
                try:
                    import win32gui
                    hwnd = window.handle
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)
                    print("✅ Focused to foreground")
                except:
                    print("✅ Focus set")
            except Exception as focus_error:
                print(f"⚠️ Focus failed: {focus_error}")
            
            # Get window position
            rect = window.rectangle()
            print(f"📍 Window position: ({rect.left}, {rect.top})")
            print(f"📏 Window size: {rect.width()} x {rect.height()}")
            
            return rect
            
        except Exception as e:
            print(f"❌ Connection failed (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"⏰ Waiting 10 seconds before retry...")
                time.sleep(10)
            else:
                print(f"💥 All retries failed, unable to connect to application")
                return None
    
    return None

def capture_screenshot(window_rect):
    """Capture window screenshot"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"login_screenshot_{timestamp}.png"
        
        screenshot = ImageGrab.grab(bbox=(
            window_rect.left,
            window_rect.top,
            window_rect.right,
            window_rect.bottom
        ))
        
        screenshot.save(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        return screenshot, screenshot_path
        
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return None, None

def format_date_for_filename(date_str):
    """Convert DD.MM format to DD-MM-YYYY format"""
    try:
        from datetime import datetime
        
        # Parse DD.MM format
        day, month = date_str.split('.')
        
        # Assume current year or next year (based on month)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # If month is less than current month, assume next year
        if int(month) < current_month:
            year = current_year + 1
        else:
            year = current_year
        
        # Format as DD-MM-YYYY
        formatted_date = f"{day.zfill(2)}-{month.zfill(2)}-{year}"
        return formatted_date
        
    except Exception as e:
        print(f"❌ Date formatting failed: {e}")
        return f"{date_str}-2024"  # Default format

def handle_save_dialog(date_str, window_rect):
    """Handle save dialog"""
    try:
        print(f"      📝 Processing date: {date_str}")
        
        # Format date for filename
        formatted_date = format_date_for_filename(date_str)
        filename = f"C:/RB2/RB2-{formatted_date}sc"
        
        print(f"      📁 Filename: {filename}")
        
        # Wait for dialog to fully load
        time.sleep(1)
        
        # Try to find filename input box (usually in center-bottom of dialog)
        # According to screenshot, filename input box should be in dialog
        dialog_center_x = window_rect.left + window_rect.width() // 2
        dialog_center_y = window_rect.top + window_rect.height() // 2
        
        # Estimated position of filename input box
        filename_input_x = dialog_center_x
        filename_input_y = dialog_center_y + 60  # Slightly below center
        
        print(f"      🎯 Click filename input box: ({filename_input_x}, {filename_input_y})")
        pyautogui.click(filename_input_x, filename_input_y)
        time.sleep(0.5)
        
        # Clear input box and enter new filename
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.typewrite(filename, interval=0.05)
        time.sleep(0.5)
        
        # Press Enter to save
        print("⌨️ Press Enter to save...")
        pyautogui.press('enter')
        
        # Wait for confirmation dialog to appear
        print("      ⏰ Waiting for confirmation dialog to appear...")
        time.sleep(3)
        
        # Handle "Data successfully exported!" confirmation dialog
        print("      ✅ Handling confirmation dialog...")
        handle_confirmation_dialog(window_rect)
        
        # Brief wait after save completion
        print("      ⏰ Save completed, waiting 2 seconds...")
        time.sleep(2)
                      
        print(f"      ✅ Save completed: {filename}.xls")
        
    except Exception as e:
        print(f"      ❌ Save handling failed: {e}")
        # If failed, try pressing ESC to close dialog
        pyautogui.press('escape')
        time.sleep(0.5)

def handle_confirmation_dialog(window_rect):
    """Handle confirmation dialog (Data successfully exported!)"""
    try:
        print("         🎯 Find and click OK button...")
        
        # According to screenshot, OK button is in center-bottom of dialog
        dialog_center_x = window_rect.left + window_rect.width() // 2
        dialog_center_y = window_rect.top + window_rect.height() // 2
        
        # Estimated position of OK button (in confirmation dialog)
        ok_button_x = dialog_center_x
        ok_button_y = dialog_center_y + 40
        
        print(f"         🖱️ Click OK button: ({ok_button_x}, {ok_button_y})")
        pyautogui.click(ok_button_x, ok_button_y)
        
        print("         ✅ Confirmation dialog handled")
        
    except Exception as e:
        print(f"         ❌ Confirmation dialog handling failed: {e}")
        # Try ESC to close
        pyautogui.press('escape')

def handle_timezone_settings(window_rect):
    """Handle timezone settings and save"""
    try:
        print("🕐 Processing timezone settings...")
        
        # Wait for settings page to fully load
        time.sleep(2)
        
        # According to screenshot, Timezone dropdown position (estimated coordinates)
        # Dropdown on right side approximately x=370, y=270
        timezone_dropdown_x = 366
        timezone_dropdown_y = 246
        
        print(f"🎯 Click timezone dropdown: ({timezone_dropdown_x}, {timezone_dropdown_y})")
        pyautogui.click(timezone_dropdown_x, timezone_dropdown_y)
        time.sleep(1.5)
        
        # Select America/Puerto_Rico timezone
        print("📍 Force select timezone: HongKong")
        
        # Method 1: Use keyboard quick search
        # Clear current input and directly enter complete timezone name
        pyautogui.click(321, 331)
        time.sleep(1)
        
        # Press Enter to confirm selection
        print("✅ Confirm selection America/Puerto_Rico")
        pyautogui.press('enter')
        time.sleep(0.5)
        
        # Click green checkmark save button in bottom right
        # According to screenshot, green checkmark button is in bottom right
        save_button_x = 1843  # Bottom right slightly left
        save_button_y = 1024  # Bottom slightly up
        
        print(f"✅ Click green checkmark save button: ({save_button_x}, {save_button_y})")
        pyautogui.click(save_button_x, save_button_y)
        time.sleep(2)
        
        # Handle "Data successfully exported!" confirmation dialog
        print("      ✅ Handling confirmation dialog...")
        handle_confirmation_dialog(window_rect)
        
        print("✅ Timezone settings saved")
        
    except Exception as e:
        print(f"❌ Timezone settings processing failed: {e}")

def encrypt_password(password):
    """Encrypt password using base64"""
    try:
        # Convert password to bytes then encode with base64
        password_bytes = password.encode('utf-8')
        encrypted = base64.b64encode(password_bytes).decode('utf-8')
        return encrypted
    except Exception as e:
        print(f"❌ Password encryption failed: {e}")
        return None

def decrypt_password(encrypted_password):
    """Decrypt base64 encoded password"""
    try:
        # Decode base64 then convert back to string
        password_bytes = base64.b64decode(encrypted_password.encode('utf-8'))
        password = password_bytes.decode('utf-8')
        return password
    except Exception as e:
        print(f"❌ Password decryption failed: {e}")
        return None

def get_credentials():
    """Get credentials with encrypted password"""
    # Default credentials - password is base64 encoded
    username = "OW078"
    encrypted_password = "TWFrYW5uYXMyQEA="  # Base64 encoded
    
    # Decrypt password
    password = decrypt_password(encrypted_password)
    if not password:
        print("❌ Failed to decrypt credentials")
        return None, None
        
    return username, password

def kill_runningball_process():
    """Terminate RunningBall.exe processes"""
    try:
        print("🔪 Terminating existing RunningBall.exe processes...")
        
        # Use taskkill command to terminate process
        import subprocess
        
        # First check if RunningBall.exe process is running
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq RunningBall.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if "RunningBall.exe" in result.stdout:
            print("   🎯 Found RunningBall.exe process, terminating...")
            
            # Force terminate RunningBall.exe
            kill_result = subprocess.run(['taskkill', '/F', '/IM', 'RunningBall.exe'], 
                                       capture_output=True, text=True, shell=True)
            
            if kill_result.returncode == 0:
                print("   ✅ RunningBall.exe process successfully terminated")
                time.sleep(2)  # Wait for process to completely close
            else:
                print(f"   ⚠️ Warning when terminating process: {kill_result.stderr}")
        else:
            print("   ℹ️ No RunningBall.exe process found")
            
    except Exception as e:
        print(f"   ❌ Error occurred when terminating process: {e}")
        print("   ℹ️ Continue running program...")

def perform_login(window_rect, username=None, password=None):
    """Execute login"""
    try:
        # Get credentials
        if username is None or password is None:
            print("🔐 Loading credentials...")
            username, password = get_credentials()
            
            if not username or not password:
                print("❌ Unable to load credentials")
                return False
        
        print(f"\n🔐 Starting login...")
        print(f"📝 Username: {username}")
        print(f"🔒 Password: {'*' * len(password) if password else 'N/A'}")
        
        # Use accurate coordinates from analysis results
        print("🎯 Using accurate coordinates from analysis...")
        
        # Input field position found from analysis (1192, 653)
        username_field = {
            'x': 1182,
            'y': 587
        }
        
        password_field = {
            'x': 1182,
            'y': 612
        }
        
        print(f"✅ Username field coordinates: ({username_field['x']}, {username_field['y']})")
        print(f"✅ Password field coordinates: ({password_field['x']}, {password_field['y']})")
        
        # Enter username
        print("📝 Enter username...")
        username_abs_x = window_rect.left + username_field['x']
        username_abs_y = window_rect.top + username_field['y']
        
        pyautogui.click(username_abs_x, username_abs_y)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.typewrite(username, interval=0.1)
        time.sleep(0.5)
        
        # Enter password
        print("🔒 Enter password...")
        password_abs_x = window_rect.left + password_field['x']
        password_abs_y = window_rect.top + password_field['y']
        
        pyautogui.click(password_abs_x, password_abs_y)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.typewrite(password, interval=0.1)
        time.sleep(0.5)
        
        # Press Enter to login
        print("⌨️ Press Enter to login...")
        pyautogui.press('enter')
        
        # Wait 60 seconds after login
        print("⏰ Wait 60 seconds after login...")
        time.sleep(35)
        
        print("✅ Login operation completed")
        
        # Click specified coordinates (370, 60)
        # print("🖱️ Click coordinates (370, 60)...")
        # click_x = 358   
        # click_y = 56
        # pyautogui.click(click_x, click_y)
        # time.sleep(1)
        
        # print("✅ SettingClick completed")
        
        # # Handle timezone settings
        # print("🕐 Start handling timezone settings...")
        # handle_timezone_settings(window_rect)
        
        # Click specified coordinates (200, 60)
        print("🖱️ Click coordinates (200, 60)...")
        click_x = 208   
        click_y = 59
        pyautogui.click(click_x, click_y)
        time.sleep(1)
        
        print("✅ CalendarClick completed")
        
        # Capture screen
        screenshot, screenshot_path = capture_screenshot(window_rect)
        if not screenshot:
            return False
            
        # Recognize dates and text coordinates
        print("📅 Attempting to recognize dates and coordinates on screen...")
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Use OCR to recognize text and coordinates
            data = pytesseract.image_to_data(gray, config='--psm 6', output_type=pytesseract.Output.DICT)
            
            print("📍 Recognized text and coordinates:")
            print("=" * 60)
            
            # Create date coordinate mapping
            date_coordinates = {}
            
            # Merge all text to find date formats with weekdays
            all_text = ' '.join([data['text'][i].strip() for i in range(len(data['text'])) if data['text'][i].strip()])
            
            import re
            
            # Find date formats with weekday abbreviations (e.g.: Tue, 23.09)
            weekday_date_pattern = r'([A-Za-z]{3}),?\s*(\d{1,2}\.\d{1,2})'
            matches = re.finditer(weekday_date_pattern, all_text)
            
            print("📅 Looking for date formats with weekdays...")
            
            for match in matches:
                weekday = match.group(1)  # Weekday abbreviation (e.g.: Tue)
                date_part = match.group(2)  # Date part (e.g.: 23.09)
                full_date = f"{weekday}, {date_part}"
                
                # Find corresponding date part coordinates in OCR data
                for i in range(len(data['text'])):
                    text = data['text'][i].strip()
                    confidence = int(data['conf'][i])
                    
                    # Check if it's a date part (e.g.: 23.09)
                    if text == date_part and confidence > 20:
                        x = data['left'][i]
                        y = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]
                        
                        # Calculate center point coordinates
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        # Calculate absolute coordinates relative to window
                        abs_x = window_rect.left + center_x
                        abs_y = window_rect.top + center_y
                        
                        date_coordinates[full_date] = {
                            'x': center_x,
                            'y': center_y,
                            'abs_x': abs_x,
                            'abs_y': abs_y,
                            'confidence': confidence,
                            'date_only': date_part
                        }
                        
                        print(f"✅ Found: {full_date} at coordinates ({center_x}, {center_y})")
                        break
            
            print("=" * 60)
            print(f"📝 Complete recognized text: {all_text}")
            
            # Display date coordinate mapping (only show date formats with weekdays)
            print("\n📅 Date coordinate mapping with weekdays:")
            print("=" * 60)
            
            # Store dates in local variables
            found_dates_list = []
            
            if date_coordinates:
                # First collect all date data
                for full_date, coords in date_coordinates.items():
                    x = coords['x']
                    y = coords['y']
                    abs_x = coords['abs_x']
                    abs_y = coords['abs_y']
                    confidence = coords['confidence']
                    date_only = coords['date_only']
                    
                    # Store dates in local variables
                    found_dates_list.append({
                        'date': date_only,
                        'full_date': full_date,
                        'x': x,
                        'y': y,
                        'abs_x': abs_x,
                        'abs_y': abs_y,
                        'confidence': confidence
                    })
                
                # Sort by date order (DD.MM format)
                def parse_date_for_sorting(date_str):
                    """Parse DD.MM format date for sorting"""
                    try:
                        day, month = date_str.split('.')
                        return (int(month), int(day))  # Sort by month first, then by date
                    except:
                        return (99, 99)  # Put unparseable dates at the end
                
                found_dates_list.sort(key=lambda x: parse_date_for_sorting(x['date']))
                
                # Display sorted dates
                print("📅 Results sorted by date order:")
                for date_info in found_dates_list:
                    date_only = date_info['date']
                    full_date = date_info['full_date']
                    x = date_info['x']
                    y = date_info['y']
                    abs_x = date_info['abs_x']
                    abs_y = date_info['abs_y']
                    confidence = date_info['confidence']
                    
                    print(f"📆 {date_only}=>X={x},Y={y} (Relative coordinates) [{full_date}]")
                    print(f"📆 {date_only}=>X={abs_x},Y={abs_y} (Absolute coordinates) [{full_date}]")
                    print(f"   🎯 Confidence: {confidence}%")
                    print("-" * 40)
                
                # Click each coordinate in date order
                print("\n🖱️ Click each coordinate in date order:")
                print("=" * 60)
                
                for i, date_info in enumerate(found_dates_list, 1):
                    date = date_info['date']
                    full_date = date_info['full_date']
                    abs_x = date_info['abs_x']
                    abs_y = date_info['abs_y']
                    
                    print(f"🎯 Click {i} date: {full_date} (in date order)")
                    print(f"   📍 coordinates: ({abs_x}, {abs_y})")
                    
                    # Click coordinates
                    pyautogui.click(abs_x, abs_y)
                    print(f"   ✅ Clicked {date}")
                    
            
                    # Then click download coordinates (60, 200)
                    print("🖱️ Click coordinates (60, 200)...")
                    click_x2 = window_rect.left + 60
                    click_y2 = window_rect.top + 200
                    pyautogui.click(click_x2, click_y2)
                    time.sleep(1)
                    
                    print("✅ Download click completed")
                    
                    
                    # Pause two seconds waiting for save dialog to appear
                    print("   ⏰ Waiting for save dialog to appear...")
                    time.sleep(2)
                    
                    # Handle save dialog
                    print("   💾 Processing save dialog...")
                    handle_save_dialog(date, window_rect)
                    
                    print("-" * 40)
                
                print(f"🎉 Completed clicking in date order {len(found_dates_list)} date")
                print(f"📋 Click order: {[d['date'] for d in found_dates_list]}")
                
            else:
                print("⚠️ No dates with weekday abbreviations found")
            
            print("=" * 60)
                        
        except ImportError:
            print("⚠️ tesseract not installed, cannot perform OCR recognition")
        except Exception as ocr_error:
            print(f"❌ OCR recognition failed: {ocr_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def cleanup_screenshots():
    """Clean up all screenshot files"""
    try:
        import os
        import glob
        
        print("🧹 Starting screenshot cleanup...")
        
        # Find all screenshot files (starting with login_screenshot_ .png files)
        screenshot_pattern = "login_screenshot_*.png"
        screenshot_files = glob.glob(screenshot_pattern)
        
        if screenshot_files:
            print(f"📸 Found {len(screenshot_files)} screenshot files:")
            
            for screenshot_file in screenshot_files:
                try:
                    os.remove(screenshot_file)
                    print(f"   ✅ Deleted: {screenshot_file}")
                except Exception as e:
                    print(f"   ❌ Deletion failed: {screenshot_file} - {e}")
            
            print(f"🎉 Screenshot cleanup completed, deleted {len(screenshot_files)} files")
        else:
            print("ℹ️ No screenshot files found for cleanup")
            
    except Exception as e:
        print(f"❌ Error occurred during screenshot cleanup: {e}")

def main():
    """Main function"""
    print("🎯 RunningBall Login Tool")
    print("=" * 40)
    
    # Configure pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
    
    try:
        clear_all_files_in_rb2()
        # 1. Connect and maximize
        window_rect = connect_and_maximize()
        if not window_rect:
            print("❌ Unable to connect to application")
            return
        
        # 2. Execute login
        success = perform_login(window_rect)
        
        print("\n" + "=" * 40)
        if success:
            print("🎉 Login process completed!")
        else:
            print("❌ Login process failed!")
        send_email_to_est()
            
    except KeyboardInterrupt:
        print("\n⏹️ User interrupted operation")
    except Exception as e:
        print(f"\n💥 Error occurred during execution: {e}")
    finally:
        # Clean up screenshots regardless of success or failure
        print("\n" + "=" * 40)
        cleanup_screenshots()
        kill_runningball_process()

if __name__ == "__main__":
    main()