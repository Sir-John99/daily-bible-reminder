import os
import requests
import datetime
import pandas as pd
import time

# Load API credentials securely from GitHub Secrets
ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN = os.getenv("GREEN_API_TOKEN")

def wait_until_exact_time(target_hour, target_minute):
    """Pauses the script until the next occurrence of 1:15 AM."""
    now = datetime.datetime.now()
    
    # Target is 1:15 AM today
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # If it's currently late at night (e.g., 9:00 PM), the target 1:15 AM belongs to tomorrow
    if now > target_time and now.hour >= 12:
        target_time += datetime.timedelta(days=1)
    # If the workflow actually runs late and loads AFTER 1:15 AM the same morning, send immediately
    elif now > target_time and now.hour < 12:
        print(f"System loaded late at {now.strftime('%H:%M:%S')}. Sending immediately.")
        return

    delay_seconds = (target_time - now).total_seconds()
    print(f"System loaded at {now.strftime('%H:%M:%S')}. Waiting {int(delay_seconds // 60)} minutes until 1:15 AM...")
    time.sleep(delay_seconds)
    print(f"Target reached! Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")

def send_whatsapp_reminder():
    # 1. Hold execution until exactly 1:15 AM
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
    
    # 5. Your Targeted WhatsApp Group ID
    CHAT_ID = "120363404249902820@g.us" 
    
    # 6. Construct the API request payload
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": CHAT_ID,
        "message": message_text
    }
    headers = {'Content-Type': 'application/json'}
    
    # 7. Send the message via Green API
    print(f"Attempting to send today's message for date: {today_str}")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Success! Daily reading reminder sent to your WhatsApp group.")
    else:
        print(f"Failed to send. Error code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    send_whatsapp_reminder()
