import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
# Replace this with your actual bot token
BOT_TOKEN = os.getenv('BOT_TOKEN')

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
            # instead of the last chat_id, please return array of chat_id that has message of /start 
            return chat_id 
        else:
            print("⚠️ No messages found. Try sending a message to your bot first.")
            return None
    else:
        print(f"❌ Failed to fetch updates. Status code: {response.status_code}")
        print(response.text)
        return None
    
def get_chat_ids_with_start():
    global BOT_TOKEN
    print(BOT_TOKEN)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch updates. Status code: {response.status_code}")
        return []

    data = response.json()
    # print(json.dumps(data, indent=2))  # Optional: see full response

    chat_ids = set()  # Use set to avoid duplicates

    for item in data.get("result", []):
        message = item.get("message")
        if message:
            text = message.get("text", "")
            if text.strip() == "/start":
                chat_id = message["chat"]["id"]
                chat_ids.add(chat_id)

    if chat_ids:
        print("✅ Found chat IDs with /start command:")
        for cid in chat_ids:
            print(f" - {cid}")
    else:
        print("⚠️ No /start messages found.")

    return list(chat_ids)

# get_chat_ids_with_start()