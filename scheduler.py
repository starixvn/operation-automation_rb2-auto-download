# Write a function to execute file runningball_login.py every hour
import os   
import glob
import schedule
import time
from datetime import datetime
import multiprocessing
TIMEOUT_SECONDS = 1 * 60 * 60  # 1 hour in seconds
def execute_runningball_logic_with_timeout():
    """Create and start a process with a timeout."""
    
    # 1. Create a child process
    process = multiprocessing.Process(target=execute_runningball_logic)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting child process. Timeout: 1 hour.")
    process.start()
    
    # 2. Wait (join) for the child process with a timeout
    process.join(timeout=TIMEOUT_SECONDS)
    
    # 3. Check the result
    if process.is_alive():
        # If the process is still alive after the join timeout
        print("\n" + "="*50)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛑 TIMEOUT! Task exceeded {TIMEOUT_SECONDS} seconds.")
        print(f"Terminating process ID: {process.pid}")
        
        # Terminate the process
        process.terminate()
        process.join() # Wait for the process to fully terminate
        print("="*50 + "\n")
        
    else:
        # The process completed before the timeout
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ Task completed within the limit.")

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
        if current_hour % 4 != 0:
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
    next_schedule = schedule.next_run()
    print(f"📅 Next scheduled execution at {next_schedule}")

def schedule_hourly_task():
    """Schedule the execute_runningball_logic function to run every hour"""
    try:
        # Schedule the task every hour
        schedule.every().hour.at(":00").do(execute_runningball_logic_with_timeout)
        
        print("⏰ Scheduled execute_runningball_logic_with_timeout to run every hour.")
        print_next_schedule()                
        while True:
            schedule.run_pending()
            time.sleep(1)
    except ImportError:
        print("❌ The 'schedule' library is not installed. Please install it using 'pip install schedule'.")
    except Exception as e:
        print(f"❌ Scheduling failed: {e}")
if __name__ == "__main__":    
    # execute_runningball_script('login_basketball.py')
    # time.sleep(120)
    # execute_runningball_script('login_tennis.py')
    # time.sleep(120)
    # execute_runningball_script('login_ice_hockey.py')
    # time.sleep(120)
    # execute_runningball_script('login_cricket.py')
    schedule_hourly_task()                
    time.sleep(60)