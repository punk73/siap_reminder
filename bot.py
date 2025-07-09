import requests
import json

# Replace this with your actual bot token
BOT_TOKEN = "7854760299:AAFvuh6EdsSHlh1cFX_hGhPzEGAnSvKwxMs"

def send_message(chat_id, message):
    """
    Send a message to a Telegram user or group.

    Parameters:
    - chat_id (str or int): The Telegram chat ID
    - message (str): The message to send
    """
    global BOT_TOKEN
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # Optional: allows bold, italic, etc.
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Message sent successfully.")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}")
        print(response.text)

def get_chat_id():
    global BOT_TOKEN
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()  # parse response JSON
        print(json.dumps(data, indent=2))  # nicely formatted

        # Optional: extract chat_id
        if "result" in data and len(data["result"]) > 0:
            chat_id = data["result"][-1]["message"]["chat"]["id"]
            print(f"✅ Your chat_id is: {chat_id}")
            return chat_id
        else:
            print("⚠️ No messages found. Try sending a message to your bot first.")
            return None
    else:
        print(f"❌ Failed to fetch updates. Status code: {response.status_code}")
        print(response.text)
        return None

# get_chat_id()