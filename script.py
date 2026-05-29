import os
import requests
import datetime
import pandas as pd

# Load API credentials securely from GitHub Secrets
ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN = os.getenv("GREEN_API_TOKEN")

def send_whatsapp_reminder():
    # 1. Read the CSV reading plan
    try:
        df = pd.read_csv("reading_plan.csv")
    except FileNotFoundError:
        print("Error: 'reading_plan.csv' file not found in repository.")
        return

    # 2. Get today's date formatted as YYYY-MM-DD
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # 3. Get today's verse text matching the date
    row = df[df['Date'] == today_str]
    if row.empty:
        print(f"Notice: No reading scheduled for today ({today_str}).")
        return
        
   message_text = row['Message'].values[0].replace('\\n', '\n')
    
    # 4. Your Targeted WhatsApp Group ID
    CHAT_ID = "120363404249902820@g.us" 
    
    # 5. Construct the API request payload
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": CHAT_ID,
        "message": message_text
    }
    headers = {'Content-Type': 'application/json'}
    
    # 6. Send the message via Green API
    print(f"Attempting to send today's message: {message_text}")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Success! Daily reading reminder sent to your WhatsApp group.")
    else:
        print(f"Failed to send. Error code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    send_whatsapp_reminder()
