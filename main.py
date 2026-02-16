"""
=====================================================
   📸 INSTAGRAM AUTO-REPLY BOT (GitHub Actions Ready)
   --------------------------------------------------
   🔥 CREDITS: Script by Praveer
   --------------------------------------------------
   FEATURES:
   - Auto-Installs its own requirements
   - "Slider" Logic (Loop Limit)
   - "Not Now" Popup Bypass
   - Scoped Message Reader (Fixes 'ritu.zii' bug)
=====================================================
"""

import os
import sys
import time
import subprocess
import random
import re
from datetime import datetime

# --- 1. AUTO-INSTALL REQUIREMENTS INSIDE CODE ---
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium_stealth import stealth
except ImportError:
    print("📦 Installing missing requirements...")
    install("selenium")
    install("selenium-stealth")
    install("webdriver-manager")
    print("✅ Requirements Installed! Restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)

# --- 2. CONFIGURATION (THE SLIDER) ---
# Secrets (Set these in GitHub Secrets or Env Vars)
COOKIE = os.environ.get("INSTA_COOKIE")
TARGET = os.environ.get("TARGET_THREAD_ID")  # Numeric ID (e.g., 887427387249300)
MESSAGES = os.environ.get("MESSAGES", "Hello|Hi|Bot Active").split("|")

# 🎚️ THE SLIDER (Loop Controls)
SLIDER_LIMIT = 1000       # How many messages to send before stopping
SLIDER_DELAY = (10, 30)   # Wait 10-30s between replies (Safety Slider)
SESSION_TIME = 600        # Restart browser every 10 mins (Memory Saver)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 {msg}", flush=True)

def get_driver():
    options = Options()
    # GitHub Actions / Headless Config
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=375,812")
    options.add_argument("--disable-notifications")
    
    # iPhone User Agent (Critical for this selector logic)
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Proxy Support (Optional)
    if os.environ.get("PROXY_URL"):
        options.add_argument(f'--proxy-server={os.environ.get("PROXY_URL")}')

    service = Service(log_output=os.devnull)
    driver = webdriver.Chrome(options=options, service=service)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Linux armv8l",
        webgl_vendor="ARM",
        renderer="Mali-G76",
        fix_hairline=True,
    )
    return driver

def close_popups(driver):
    """Closes 'Not Now', 'Save Info', 'Add to Home'"""
    try:
        xpath = "//button[contains(text(), 'Not Now')] | //button[contains(text(), 'Not now')] | //button[contains(text(), 'Cancel')]"
        for btn in driver.find_elements(By.XPATH, xpath):
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)
    except: pass

def get_last_message(driver):
    """
    Reads the last message bubble.
    Scopes to <main> to avoid reading the header/username.
    """
    IGNORE = ["Not Now", "Seen", "Active", "Save info", "Double tap", "The link you followed"]
    try:
        # Scoped Selector (Fixes 'ritu.zii' bug)
        elements = driver.find_elements(By.XPATH, "//main//div[contains(@role, 'row')]//div[contains(@dir, 'auto')]")
        if not elements:
            elements = driver.find_elements(By.XPATH, "//main//div[contains(@class, 'x')]//span")
            
        if elements:
            for i in range(1, min(len(elements), 5) + 1):
                text = elements[-i].text.strip()
                if not text: continue
                if any(bad in text for bad in IGNORE): continue
                return text
    except: pass
    return ""

def send_msg(driver, text):
    try:
        box = driver.find_element(By.XPATH, "//div[@role='textbox'][contains(@contenteditable, 'true')]")
        driver.execute_script("arguments[0].focus();", box)
        driver.execute_script(f"document.execCommand('insertText', false, '{text}');")
        box.send_keys(" ") 
        time.sleep(0.5)
        box.send_keys(Keys.ENTER)
        return True
    except: return False

def main():
    print("=========================================")
    print("   🔥 INSTA BOT STARTED | BY PRAVEER 🔥   ")
    print("=========================================")

    if not COOKIE or not TARGET:
        log("❌ Error: Missing ENV Variables (INSTA_COOKIE or TARGET_THREAD_ID)")
        sys.exit(1)

    sent_count = 0
    
    # Clean Target URL Logic
    target_id = re.sub(r'\D', '', TARGET) if "/t/" not in TARGET else re.search(r'/t/(\d+)', TARGET).group(1)
    url = f"https://www.instagram.com/direct/t/{target_id}/"
    log(f"🎯 Target Locked: {url}")

    while sent_count < SLIDER_LIMIT:
        driver = None
        try:
            log("🚀 Launching Browser...")
            driver = get_driver()
            
            # 1. Login via Cookie
            driver.get("https://www.instagram.com/")
            driver.add_cookie({'name': 'sessionid', 'value': COOKIE, 'domain': '.instagram.com', 'path': '/'})
            driver.refresh()
            time.sleep(5)

            # 2. Go to Thread
            driver.get(url)
            time.sleep(5)
            close_popups(driver)

            last_msg = get_last_message(driver)
            log(f"✅ Connected. Last msg seen: '{last_msg}'")
            
            session_start = time.time()

            # 3. Listen Loop (The Slider)
            while (time.time() - session_start) < SESSION_TIME:
                if sent_count >= SLIDER_LIMIT: break

                current_msg = get_last_message(driver)
                
                if current_msg and current_msg != last_msg:
                    log(f"📩 Incoming: {current_msg}")
                    
                    # Wait (Slider Delay)
                    wait_time = random.randint(*SLIDER_DELAY)
                    time.sleep(wait_time)
                    
                    reply = random.choice(MESSAGES)
                    if send_msg(driver, reply):
                        sent_count += 1
                        log(f"📤 Sent ({sent_count}/{SLIDER_LIMIT}): {reply}")
                        last_msg = reply 
                        
                        # Verify UI update
                        time.sleep(2)
                        check = get_last_message(driver)
                        if check: last_msg = check
                
                time.sleep(2) # Check frequency

        except Exception as e:
            log(f"⚠️ Crash: {e}")
        finally:
            if driver: driver.quit()
            log("♻️ Restarting Session (Memory Cleanup)...")
            time.sleep(5)

    log("🏁 Slider Limit Reached. Bye Praveer!")

if __name__ == "__main__":
    main()
