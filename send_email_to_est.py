
import os
import glob
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_to_est(sport_name):    
    SENDER_EMAIL = "jacob.phan@starixsoft.com"
    # WARNING: App Passwords should ideally be stored securely (e.g., using environment variables).
    SENDER_PASSWORD = os.getenv("JACOB_APP_PASSWORD", "") 
    RECEIVER_EMAIL = [
        "levi.vu@starixsoft.com", 
        "jacob.phan@starixsoft.com", 
        "toby.phan@starixsoft.com",
        "richard.truong@starixsoft.com",    
        "7racychieng@gmail.com",
        "rdrd33@gmail.com"
    ]
    #RECEIVER_EMAIL = ["jacob.phan@starixsoft.com"]
    
    ATTACHMENT_DIR = "C:/RB2/Combined"
    SUBJECT = f"RB2 Excel for {sport_name}"
    BODY_MESSAGE = "Dear EST,\n\nPlease find attached all RB2 Excel files \n\nBest regards,\nJacob"
    # --------------------
    """
    Connects to Gmail's SMTP server, finds all Excel files in the specified 
    directory, attaches them, and sends the email.
    """
    print(f"Starting email process from {SENDER_EMAIL} to {', '.join(RECEIVER_EMAIL)}...")
    
    # 1. Find all Excel files in the directory
    # Searches for .xls, .xlsx, and .xlsm files
    search_path = os.path.join(ATTACHMENT_DIR, "*.xls*")
    excel_files = glob.glob(search_path)
    excel_files.append("C:/RB2/Combined/RB2.zip")
    
    print(f"APP_PASSWORD: {SENDER_PASSWORD} ")
    if not os.path.isdir(ATTACHMENT_DIR):
        print(f"Error: Directory '{ATTACHMENT_DIR}' does not exist.")
        return
    
    if not excel_files:
        print(f"Warning: No Excel files found in '{ATTACHMENT_DIR}'")
        return
    else:
        print(f"Found {len(excel_files)} Excel file(s) to attach.")

    # 2. Setup the MIME message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAIL)  # Convert list to comma-separated string for header
    msg['Subject'] = SUBJECT
    
    # Attach the text body. Using 'utf-8' for Vietnamese character support.
    msg.attach(MIMEText(BODY_MESSAGE, 'plain', 'utf-8'))

    # 3. Attach files
    for filepath in excel_files:
        try:
            with open(filepath, 'rb') as f:
                # Create a MIMEApplication part
                part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
            
            # Add header for file attachment
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            msg.attach(part)
            print(f"Attached: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Could not attach file {filepath}: {e}")

    # 4. Connect to SMTP server and send email
    try:
        # Use Gmail's SMTP server and port 587 (TLS encryption)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        
        # Log in to account using App Password
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send the email
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        
        print("\nSUCCESS: Email sent successfully!")
        
    except smtplib.SMTPAuthenticationError:
        print("\nERROR: SMTP Authentication Failed. Check your SENDER_EMAIL and SENDER_PASSWORD (App Password).")
    except Exception as e:
        print(f"\nAn error occurred while sending the email: {e}")
    finally:
        if 'server' in locals():
            server.quit()

if __name__ == "__main__":
    send_email_to_est()