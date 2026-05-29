import os
import requests
import datetime
import pandas as pd

# Load API credentials securely from GitHub Secrets
ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN = os.getenv("GREEN_API_TOKEN")

# Function to find your Group ID automatically if you don't know it yet
def find_group_id():
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/getChats/{API_TOKEN}"
    try:
        response = requests.get(url).json()
        print("--- LOOKING FOR YOUR BIBLE STUDY GROUP ID ---")
        for chat in response:
            # Change "Bible Study" below to a word in your actual WhatsApp Group Name!
            if "Bible" in chat.get("name", "") or chat.get("type") == "group":
                print(f"FOUND GROUP: Name: {chat.get('name')} | ID: {chat.get('id')}")
        print("--------------------------------------------")
    except Exception as e:
        print("Could not retrieve chats:", e)

def send_whatsapp_reminder():
    # 1. Read the CSV reading plan
    df = pd.read_csv("reading_plan.csv")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # 2. Get today's verse text
    row = df[df['Date'] == today_str]
    if row.empty:
        print(f"No reading scheduled for today ({today_str}).")
        return
        
    message_text = row['Message'].values[0]
    
    # 3. SET YOUR GROUP ID HERE once found (or leave as template to test search)
    # Paste your 120363xxxxxxxxx@g.us ID here once you know it!
    CHAT_ID = "120363024857395274@g.us" 
    
    # 4. Construct the API request payload
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": CHAT_ID,
        "message": message_text
    }
    headers = {'Content-Type': 'application/json'}
    
    # 5. Send the message via Green API
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Successfully sent daily reading reminder to WhatsApp group!")
    else:
        print(f"Failed to send. Error code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    # This prints out your group IDs to the logs so you can copy the correct one!
    find_group_id() 
    # This attempts to execute the message delivery
    send_whatsapp_reminder()
