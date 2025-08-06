# index.py

def run_main():
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
    from bot import send_message, get_chat_ids_with_start, get_chat_id
    from dotenv import load_dotenv
    import os

    load_dotenv()

    BEARER_TOKEN = os.getenv("BEARER_TOKEN")
    EXP_TOKEN = os.getenv("EXP_TOKEN")

    if os.name == 'nt':
        CHROMEDRIVER_PATH = "driver/chromedriver.exe"
    elif os.name == 'posix' and os.uname().sysname == 'Darwin':
        CHROMEDRIVER_PATH = "driver/chromedriver"
    elif os.name == 'posix' and os.uname().sysname == 'Linux':
        CHROMEDRIVER_PATH = "driver/chromedriver_linux"
    else:
        CHROMEDRIVER_PATH = "driver/chromedriver"

    TARGET_URL = "https://siap.bkpsdm.karawangkab.go.id/gallery?view=full"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://siap.bkpsdm.karawangkab.go.id")
    time.sleep(1)

    driver.execute_script(f"""
    localStorage.setItem("auth._token.local", "Bearer {BEARER_TOKEN}");
    localStorage.setItem("auth._token_expiration.local", "{EXP_TOKEN}");
    localStorage.setItem("auth.strategy", "local");
    """)
    print("✅ Token injected.")

    driver.get(TARGET_URL)

    sleepTime = 3
    try:
        first_thumb = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v-responsive__content"))
        )
        print("✅ Thumbnail found. Clicking to reveal full content...")
        time.sleep(sleepTime)
        first_thumb.click()
    except Exception as e:
        print(f"❌ Error clicking thumbnail: {e}")
        driver.quit()
        return "Terjadi kesalahan saat mengakses data."

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v-list-item__title"))
        )
        time.sleep(sleepTime)
    except:
        print("⚠️ Timeout: Titles not found.")
        driver.quit()
        return "Gagal memuat data absensi."

    soup = BeautifulSoup(driver.page_source, "html.parser")
    titles = soup.select(".v-list-item__title")
    subtitles = soup.select(".v-list-item__subtitle")

    appearance_count = {}
    last_record_by_name = {}

    for t, s in zip(titles, subtitles):
        name = t.get_text(strip=True)
        nip = s.get_text(strip=True)
        appearance_count[name] = appearance_count.get(name, 0) + 1
        last_record_by_name[name] = {"name": name, "nip": nip}

    data = []
    belum_absen = []
    for name, record in last_record_by_name.items():
        count = appearance_count.get(name, 0)
        record["absence"] = "belum absen pulang" if count == 1 else "sudah absen pulang"
        record["is_ok"] = 0 if count == 1 else 1
        data.append(record)
        if not record["is_ok"]:
            belum_absen.append(record)

    with open("belum_absen.txt", "w", encoding="utf-8") as f:
        total = len(belum_absen)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Total belum absen: {total}, diantaranya (update : {timestamp}):\n")
        for i, person in enumerate(belum_absen, 1):
            f.write(f"{i}. {person['name']} - {person['nip']}\n")

    with open("belum_absen.txt", "r", encoding="utf-8") as f:
        message = f.read()

    # within main.py
    # chat_ids = get_chat_ids_with_start() # i pull chat id here, how get the chat id from bot instead ???
    # for chat_id in chat_ids:
    #     send_message(chat_id, message)

    driver.quit()
    return message  # <-- Return message so bot can reply it