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
from login_base import connect_and_maximize, perform_login, cleanup_screenshots, kill_runningball_process, download_all_excel_files

def choose_sport():
    print("Choose Ice Hockey:")
    time.sleep(5)
    pyautogui.click(1175, 555)
    time.sleep(2)
    pyautogui.click(1175, 632)
    time.sleep(2)
def main():
    """Main function"""
    print("🎯 Ice Hockey Login Tool")
    print("=" * 40)
    
    # Configure pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
    
    try:
        clean_all_files_in_rb2()
        # 1. Connect and maximize
        window_rect = connect_and_maximize()        
        if not window_rect:
            print("❌ Unable to connect to application")
            return
        
        choose_sport()
        # 2. Execute login
        success = perform_login(window_rect)
        
        print("\n" + "=" * 40)
        if success:
            print("🎉 Login process completed!")
        else:
            print("❌ Login process failed!")
        
        # 3. Download all other sports data
        download_all_excel_files(window_rect)
        print("\n" + "=" * 40)                    
        print("Download all other sports data completed!")
        
        # 4. Execute rb2 helper
        execute_rb2_helper('i.hockey')
        send_email_to_est("Ice Hockey")
            
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