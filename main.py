from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from bot import send_message

# === CONFIG ===
BEARER_TOKEN = "22c4bf90-45d7-11f0-ab45-0f32a702e16c"
CHROMEDRIVER_PATH = "driver/chromedriver"
TARGET_URL = "https://siap.bkpsdm.karawangkab.go.id/gallery?view=full"

# === SETUP SELENIUM ===
options = Options()
options.add_argument("--headless")  # Enable if you want background mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# STEP 1: Inject token
driver.get("https://siap.bkpsdm.karawangkab.go.id")
time.sleep(1)

driver.execute_script(f"""
localStorage.setItem("auth._token.local", "Bearer {BEARER_TOKEN}");
localStorage.setItem("auth._token_expiration.local", "1752137075536");
localStorage.setItem("auth.strategy", "local");
""")
print("✅ Token injected.")

# STEP 2: Go to ?view=full page
driver.get(TARGET_URL)

# STEP 3: Wait for the first .v-responsive__content and click it
try:
    first_thumb = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "v-responsive__content"))
    )
    print("✅ Thumbnail found. Clicking to reveal full content...")
    time.sleep(0.5)
    first_thumb.click()
except Exception as e:
    print(f"❌ Error clicking thumbnail: {e}")
    driver.quit()
    exit()

# STEP 4: Wait for titles and subtitles to appear
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "v-list-item__title"))
    )
    time.sleep(1)  # wait for all to render
except:
    print("⚠️ Timeout: Titles not found.")
    driver.quit()
    exit()

# STEP 5: Parse page content with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")
titles = soup.select(".v-list-item__title")
subtitles = soup.select(".v-list-item__subtitle")

data = []

appearance_count = {}
last_record_by_name = {}

# Loop over all entries
for t, s in zip(titles, subtitles):
    name = t.get_text(strip=True)
    nip = s.get_text(strip=True)

    # Count the number of times this name appears
    appearance_count[name] = appearance_count.get(name, 0) + 1

    # Store the last occurrence of this name
    last_record_by_name[name] = {
        "name": name,
        "nip": nip
        # We will add "absence" later
    }

# Now build final data list and set absence status
data = []
belum_absen = []
for name, record in last_record_by_name.items():
    count = appearance_count.get(name, 0)
    record["absence"] = "belum absen pulang" if count == 1 else "sudah absen pulang"
    record["is_ok"] = 0 if count == 1 else 1
    data.append(record)
    if not record["is_ok"]:
        belum_absen.append(record)
# STEP 6: Save to JSON
with open("gallery_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

with open("belum_absen.json", "w", encoding="utf-8") as f:
    json.dump(belum_absen, f, indent=2, ensure_ascii=False)

# make text file total belum absen: xxx, diantaranya:
# 1. name - nip
# STEP 7: Write summary to text file
with open("belum_absen.txt", "w", encoding="utf-8") as f:
    total = len(belum_absen)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # add current timestamp please
    f.write(f"Total belum absen: {total}, diantaranya (update : {timestamp}):\n")
    for i, person in enumerate(belum_absen, 1):
        f.write(f"{i}. {person['name']} - {person['nip']}\n")

print(f"\n✅ Extracted {len(data)} items and saved to gallery_data.json")

# (Optional) Save full HTML
with open("index.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

# I want to send belum_absen as text/string, how do i do that ?
# Read file contents as string
with open("belum_absen.txt", "r", encoding="utf-8") as f:
    message = f.read()

chat_id = 1829886352
# Send via Telegram
send_message(chat_id, message)

driver.quit()