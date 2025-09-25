#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Adjustment Tool - Add 12 hours to G column times in Excel files
"""

import pandas as pd
import os
import glob
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def adjust_time_in_column_g(file_path):
    """Process G column time in a single file, add 12 hours"""
    try:
        print(f"📁 Processing file: {os.path.basename(file_path)}")
        
        # Reading Excel file
        df = pd.read_excel(file_path)
        
        print(f"   📊 File size: {len(df)} row, {len(df.columns)} columns")
        print(f"   📝 Column names: {list(df.columns)}")
        
        # Check if there is G column (7th column, index 6)
        if len(df.columns) <= 6:
            print(f"   ⚠️ File only has {len(df.columns)} columns, no G column")
            return False
            
        # Get G column (index 6)
        g_column = df.iloc[:, 6]  # 7th column (G column)
        column_name = df.columns[6]
        
        print(f"   🎯 Processing G column: '{column_name}'")
        print(f"   📅 First 5 values in G column: {g_column.head().tolist()}")
        
        # Record original values
        original_values = g_column.copy()
        modified_count = 0
        
        # Process time in each row
        for idx in range(len(g_column)):
            original_value = g_column.iloc[idx]
            
            # Skip null values
            if pd.isna(original_value):
                continue
                
            try:
                # Try to parse time
                if isinstance(original_value, str):
                    # Handle special format: "23.09.2025 - 10:00"
                    if ' - ' in original_value:
                        # Split date and time parts
                        date_part, time_part = original_value.split(' - ')
                        
                        # Parse date part "23.09.2025"
                        day, month, year = date_part.split('.')
                        
                        # Parse time part "10:00"
                        hour, minute = time_part.split(':')
                        
                        # Create datetime object
                        from datetime import datetime as dt
                        time_obj = dt(
                            year=int(year),
                            month=int(month), 
                            day=int(day),
                            hour=int(hour),
                            minute=int(minute)
                        )
                    elif ':' in original_value:
                        # Might be pure time format like "14:30:00" or "14:30"
                        time_obj = pd.to_datetime(original_value, format='%H:%M:%S')
                    else:
                        # Try other formats
                        time_obj = pd.to_datetime(original_value)
                elif isinstance(original_value, datetime):
                    # Already a datetime object
                    time_obj = original_value
                else:
                    # Try to convert
                    time_obj = pd.to_datetime(original_value)
                
                # Add 12 hours
                new_time = time_obj + timedelta(hours=12)
                
                # Format back to original format "DD.MM.YYYY - HH:MM"
                if isinstance(original_value, str) and ' - ' in original_value:
                    formatted_new_time = new_time.strftime("%d.%m.%Y - %H:%M")
                    df.iloc[idx, 6] = formatted_new_time
                else:
                    df.iloc[idx, 6] = new_time
                
                modified_count += 1
                
                # Show first few modification examples
                if modified_count <= 3:
                    final_value = formatted_new_time if isinstance(original_value, str) and ' - ' in original_value else new_time
                    print(f"   ✅ Row {idx+1}: {original_value} → {final_value}")
                    
            except Exception as e:
                print(f"   ⚠️ Row {idx+1} unable to parse time: {original_value} - {e}")
                continue
        
        if modified_count > 0:
            # Create backup filename: filename_bak_ddMMyyyy.xls
            from datetime import datetime
            today = datetime.now().strftime("%d%m%Y")
            
            # Get filename (without path and extension)
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(file_name)[0]
            
            # Create backup file path: filename_bak_ddMMyyyy.xls
            backup_filename = f"{name_without_ext}_bak_{today}.xls"
            backup_path = os.path.join(file_dir, backup_filename)
            
            # Always rename original file to backup (overwrite if exists)
            import shutil
            if os.path.exists(backup_path):
                print(f"   🔄 Overwriting existing backup: {backup_filename}")
            shutil.move(file_path, backup_path)
            print(f"   💾 Original file renamed to: {backup_filename}")
            
            # Save modified file to original filename (Keep original format)
            df.to_excel(file_path, index=False, engine='openpyxl')
            print(f"   ✅ Updated {modified_count} time values to original file")
            
            # Show first 5 values after modification
            print(f"   📅 First 5 values in G column after modification: {df.iloc[:, 6].head().tolist()}")
            
            return True
        else:
            print(f"   ℹ️ No processable time values found in G column")
            return False
            
    except Exception as e:
        print(f"   ❌ File processing failed: {e}")
        return False

def process_all_rb2_files():
    """Process all .xls files in C:/RB2 directory"""
    try:
        print("🚀 Starting to process RB2 files...")
        print("=" * 60)
        
        # Find all .xls files starting with RB2
        file_pattern = "C:/RB2/RB2-*sc.xls"
        files = glob.glob(file_pattern)
        
        # Filter out backup files (including _backup and _bak)
        files = [f for f in files if not f.endswith('_bak') and '_backup' not in f and '_bak_' not in f]
        
        if not files:
            print("❌ No files found matching criteria")
            return
        
        print(f"📁 Found {len(files)} files:")
        for file in files:
            print(f"   - {os.path.basename(file)}")
        
        print("\n" + "=" * 60)
        
        # Process each file
        success_count = 0
        for file_path in files:
            if adjust_time_in_column_g(file_path):
                success_count += 1
            print("-" * 40)
        
        print("=" * 60)
        print(f"🎉 Processing completed! Successfully processed {success_count}/{len(files)} files")
        
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")

def main():
    """Main function"""
    print("⏰ Excel G Column Time Adjustment Tool")
    print("📝 Function: Add 12 hours to all times in G column")
    print("=" * 60)
    
    # Check if pandas is installed
    try:
        import pandas as pd
        print(f"✅ pandas version: {pd.__version__}")
    except ImportError:
        print("❌ Please install pandas first: pip install pandas openpyxl")
        return
    
    # Process all files
    process_all_rb2_files()

if __name__ == "__main__":
    main()
