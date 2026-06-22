import os
import requests
import datetime
import pandas as pd
import time

# Load API credentials securely from GitHub Secrets
ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN = os.getenv("GREEN_API_TOKEN")

def wait_until_exact_time(target_hour, target_minute):
    """Pauses the script safely, ensuring it never hits GitHub's 6-hour timeout limit."""
    now = datetime.datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # 1. If it's late evening/night, the target 1:15 AM belongs to tomorrow morning
    if now > target_time and now.hour >= 12:
        target_time += datetime.timedelta(days=1)
        
    # 2. If it loads AFTER 1:15 AM the same morning, send immediately
    elif now > target_time and now.hour < 12:
        print(f"System loaded at {now.strftime('%H:%M:%S')} (past target). Sending immediately.")
        return

    # Calculate exact wait time
    delay_seconds = (target_time - now).total_seconds()
    
    # 3. SAFETY VALVES: If wait is too long (over 4.5 hours) or negative, don't sleep.
    # This completely prevents daytime manual runs from freezing for 6 hours!
    if delay_seconds > 16200 or delay_seconds <= 0:
        print(f"Manual run or extended delay detected ({int(delay_seconds // 60)} mins). Bypassing countdown and sending now.")
        return

    print(f"System loaded at {now.strftime('%H:%M:%S')}. Waiting {int(delay_seconds // 60)} minutes until 1:15 AM...")
    time.sleep(delay_seconds)
    print(f"Target reached! Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")

def send_whatsapp_reminder():
    # 1. Handle timing control safely
    wait_until_exact_time(1, 15)

    # 2. Read the CSV reading plan
    try:
        df = pd.read_csv("reading_plan.csv")
    except FileNotFoundError:
        print("Error: 'reading_plan.csv' file not found in repository.")
        return

    # 3. Get today's date formatted as YYYY-MM-DD
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # 4. Get today's verse text matching the date
    row = df[df['Date'] == today_str]
    if row.empty:
        print(f"Notice: No reading scheduled for today ({today_str}).")
        return
        
    # Unpack formatting markers into actual line breaks
    message_text = row['Message'].values[0].replace('\\n', '\n')
    
    # 5. Targeted WhatsApp Group ID
    CHAT_ID = "120363404249902820@g.us" 
    
    # 6. Construct the API request payload
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": CHAT_ID,
        "message": message_text
    }
    headers = {'Content-Type': 'application/json'}
    
    # 7. Send the message with a strict 30-second network timeout flag
    print(f"Attempting to send today's message for date: {today_str}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            print("Success! Daily reading reminder sent to your WhatsApp group.")
        else:
            print(f"Failed to send. Error code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.Timeout:
        print("Error: The connection to Green API timed out after 30 seconds.")

if __name__ == "__main__":
    send_whatsapp_reminder()
