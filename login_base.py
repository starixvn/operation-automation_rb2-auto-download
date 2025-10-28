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
import pygetwindow as gw
import pyautogui
import time
from PIL import ImageGrab
import cv2
import numpy as np
from datetime import datetime
import base64
from send_email_to_est import send_email_to_est
from helper_command import execute_rb2_helper, clean_all_files_in_rb2
def connect_and_maximize():
    
    """Connect to application and maximize, retry 3 times on failure"""
    app_path = r"C:\Program Files (x86)\Runningball Sports Information\Runningball Trader Client\RunningBall.exe"
    max_retries = 10
    
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

def handle_save_dialog(index, window_rect):
    """Handle save dialog"""
    try:
        print(f"      📝 Processing date: {index}")
        
        # Format date for filename
        
        filename = f"C:/RB2/RB2-{index}"
        
        print(f"      📁 Filename: {filename}")
        
        loop_wait_save_window = True
        while loop_wait_save_window:
            windows = gw.getWindowsWithTitle('Save')
            if windows and len(windows) > 0:
                loop_wait_save_window = False
            else:
                time.sleep(0.2)

        win = windows[0]
                
        # Try to find filename input box (usually in center-bottom of dialog)
        # According to screenshot, filename input box should be in dialog
        dialog_center_x = window_rect.left + window_rect.width() // 2
        dialog_center_y = window_rect.top + window_rect.height() // 2
        
        # Estimated position of filename input box
        filename_input_x = win.left + 130
        filename_input_y = win.top + 295
        
        print(f"      🎯 Click filename input box: ({filename_input_x}, {filename_input_y})")        
        time.sleep(1)
        pyautogui.click(filename_input_x, filename_input_y)
        time.sleep(1)
        
        # Clear input box and enter new filename
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.typewrite(filename, interval=0.05)
        time.sleep(1)
        
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
        time.sleep(1)
                      
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
        time.sleep(1)
        pyautogui.click(ok_button_x, ok_button_y)
        time.sleep(1)
        print("         ✅ Confirmation dialog handled")
        
    except Exception as e:
        print(f"         ❌ Confirmation dialog handling failed: {e}")
        # Try ESC to close
        pyautogui.press('escape')

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
        
        time.sleep(1)
        pyautogui.click(username_abs_x, username_abs_y)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.typewrite(username, interval=0.1)
        time.sleep(0.5)
        
        # Enter password
        print("🔒 Enter password...")
        password_abs_x = window_rect.left + password_field['x']
        password_abs_y = window_rect.top + password_field['y']
        
        time.sleep(1)
        pyautogui.click(password_abs_x, password_abs_y)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.typewrite(password, interval=0.1)
        time.sleep(0.5)
        
        # Press Enter to login
        print("⌨️ Press Enter to login...")
        pyautogui.press('enter')
        
        # Wait 60 seconds after login
        print("⏰ Wait 60 seconds after login...")
        time.sleep(60)
        
        print("✅ Login operation completed")
                
        # Click specified coordinates (200, 60)
        print("🖱️ Click coordinates (200, 60)...")
        click_x = 208   
        click_y = 59
        time.sleep(1)
        pyautogui.click(click_x, click_y)
        time.sleep(1)
        
        print("✅ CalendarClick completed")
        
        # Capture screen
        screenshot, screenshot_path = capture_screenshot(window_rect)
        if not screenshot:
            return False
            
        
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def download_all_excel_files(window_rect):
    import datetime
    print("📅 Attempting to download all excel files for other sports...")
    print("Downloading data for week 1...")
    download_all_data_for_a_week(window_rect, 1)

    # click next 7 times
    for i in range(7):
        pyautogui.click(1870, 170)
        time.sleep(1)

    print("Downloading data for week 2...")
    download_all_data_for_a_week(window_rect, 8)
    print("✅ Download all excel files for other sports completed")

def download_all_data_for_a_week(window_rect, index):
    # Recognize dates and text coordinates
    print("📅 Attempting to download all excel files for a week...")
    try:
        print("=" * 60)
        download_data(185, 175, index, window_rect)
        download_data(440, 175, index + 1, window_rect)
        download_data(695, 175, index + 2, window_rect)
        download_data(950, 175, index + 3, window_rect)
        download_data(1205, 175, index + 4, window_rect)
        download_data(1460, 175, index + 5, window_rect)
        download_data(1715, 175, index + 6, window_rect)
                
        print("=" * 60)
                        
    except Exception as e:
        print(f"❌ Error occurred: {e} when try downloading data")

def download_data(x, y, index, window_rect) :
    print(f"🖱️ Click coordinates ({x}, {y}) for date {index}")
    time.sleep(1)
    pyautogui.click(x, y)
    time.sleep(1)
    
    
    # Then click download coordinates (60, 200)
    print("🖱️ Click coordinates (47, 127) on download button...")
        
    pyautogui.click(60, 200)    
    
    print("✅ Download click completed")
            
    # Handle save dialog
    print("   💾 Processing save dialog...")
    handle_save_dialog(index, window_rect)

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
