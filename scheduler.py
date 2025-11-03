# Write a function to execute file runningball_login.py every hour
import os   
import glob
import schedule
import time
from datetime import datetime

def execute_runningball_script(python_file_name):
    script_path = os.path.join(os.path.dirname(__file__), python_file_name)
    if os.path.isfile(script_path):
        os.system(f'python "{script_path}"')
        print("✅ runningball_login.py executed successfully.")
    else:
        print(f"❌ Script not found: {script_path}")
    # Check for xlsx files in C:/RB2/Combined directory
    xlsx_files = glob.glob("C:/RB2/Combined/*.xlsx")
    if not xlsx_files:
        print("No xlsx files found in C:/RB2/Combined. Running script again...")  

def execute_runningball_logic():
    """Execute runningball_login.py every hour"""
    try:
        # Get current hour and minute
        now = datetime.now()        
        current_minute = now.minute
        current_hour = now.hour
        if current_hour != 5:
            print_next_schedule()
            return
                                      
        execute_runningball_script('login_basketball.py')
        time.sleep(120)
        execute_runningball_script('login_tennis.py')
        time.sleep(120)
        execute_runningball_script('login_ice_hockey.py')
        time.sleep(120)
        execute_runningball_script('login_cricket.py')
                                      
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
        schedule.every().hour.at(":00").do(execute_runningball_logic)
                
        print("⏰ Scheduled execute_runningball_logic to run every hour.")
        print_next_schedule()                
        while True:
            schedule.run_pending()
            time.sleep(1)
    except ImportError:
        print("❌ The 'schedule' library is not installed. Please install it using 'pip install schedule'.")
    except Exception as e:
        print(f"❌ Scheduling failed: {e}")
if __name__ == "__main__":    
           
    schedule_hourly_task()                
    time.sleep(60)