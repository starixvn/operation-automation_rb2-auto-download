# Write a function to execute file runningball_login.py every hour
import os   
import glob
import schedule
import time
from datetime import datetime

def execute_runningball_logic():
    """Execute runningball_login.py every hour"""
    try:
        # Get current hour and minute
        now = datetime.now()        
        current_minute = now.minute
        if current_minute != 0:
            print_next_schedule()
            return

        script_path = os.path.join(os.path.dirname(__file__), 'runningball_login.py')
        if os.path.isfile(script_path):
            os.system(f'python "{script_path}"')
            print("✅ runningball_login.py executed successfully.")
        else:
            print(f"❌ Script not found: {script_path}")
    except Exception as e:
        print(f"❌ Failed to execute runningball_login.py: {e}")

def print_next_schedule():
    """Print information about the next scheduled task"""
    # get the next hour
    now = datetime.now()
    current_hour = now.hour
    next_hour = (current_hour + 1) % 24
    print(f"📅 Next scheduled execution at {next_hour:02d}:00")

def schedule_hourly_task():
    """Schedule the execute_runningball_logic function to run every hour"""
    try:
        # Schedule the task every hour
        schedule.every().minute.do(execute_runningball_logic)
                
        print("⏰ Scheduled execute_runningball_logic to run every hour.")
                
        while True:
            schedule.run_pending()
            time.sleep(1)
    except ImportError:
        print("❌ The 'schedule' library is not installed. Please install it using 'pip install schedule'.")
    except Exception as e:
        print(f"❌ Scheduling failed: {e}")
if __name__ == "__main__":
    schedule_hourly_task()                
