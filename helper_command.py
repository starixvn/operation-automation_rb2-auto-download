import subprocess
import os
import glob

def execute_rb2_helper():
    command= 'C:/RB2/Tools/RB2Helper/RB2Helper.exe'
    try:
        subprocess.run(command, check=True)
        print("✅ RB2Helper.exe executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to execute RB2Helper.exe: {e}")

def clean_all_files_in_rb2():
    """
    Clean all files in the C:/RB2 directory (excluding subdirectories and their contents)
    Only deletes files in the root directory, preserves all subdirectories
    """
    directory = "C:/RB2"
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"❌ Directory {directory} does not exist.")
        return
    
    try:
        deleted_count = 0
        # Get all items in the directory
        items = os.listdir(directory)
        
        for item in items:
            item_path = os.path.join(directory, item)
            
            # Only delete if it's a file (not a directory)
            if os.path.isfile(item_path):
                try:
                    os.remove(item_path)
                    print(f"🗑️  Deleted file: {item}")
                    deleted_count += 1
                except Exception as file_error:
                    print(f"❌ Failed to delete file {item}: {file_error}")
            else:
                print(f"📁 Skipped directory: {item}")
        
        print(f"✅ Cleanup completed. {deleted_count} files deleted from {directory}")
        print(f"📂 Subdirectories and their contents were preserved.")
        
    except Exception as e:
        print(f"❌ Failed to clean files in {directory}: {e}")