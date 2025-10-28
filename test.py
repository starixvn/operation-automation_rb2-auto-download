import datetime

def calculate_next_two_sundays_info():
    
    today = datetime.date.today()
    print(f"Ngày hiện tại: {today}\n")
        
    day_of_week = today.weekday()    
    days_until_next_sunday = (6 - day_of_week)    
    first_sunday = today + datetime.timedelta(days=days_until_next_sunday)        
    second_sunday = first_sunday + datetime.timedelta(days=7)
    
    days_to_first_sunday = (first_sunday - today).days
        
    days_to_second_sunday = (second_sunday - today).days

    # --- In kết quả ---
    
    print("--- Thông tin Chủ Nhật tuần 1 ---")
    print(f"Ngày Chủ Nhật đầu tiên: {first_sunday}")
    print(f"Số ngày kể từ hiện tại tới Chủ Nhật này: {days_to_first_sunday} ngày")
    
    print("\n--- Thông tin Chủ Nhật tuần 2 ---")
    print(f"Ngày Chủ Nhật thứ hai: {second_sunday}")
    print(f"Số ngày kể từ hiện tại tới Chủ Nhật này: {days_to_second_sunday} ngày")

# Chạy hàm
calculate_next_two_sundays_info()