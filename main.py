"""
=====================================================
   📸 INSTAGRAM AUTO-REPLY BOT (GitHub Actions Ready)
   --------------------------------------------------
   🔥 CREDITS: Script by Praveer
   --------------------------------------------------
   FEATURES:
   - Auto-Installs requirements
   - Slider Logic (Limit & Delay)
   - Robust Cookie Injection (Fixes 'unable to set cookie')
=====================================================
"""

import os
import sys
import time
import subprocess
import random
import re
from datetime import datetime

# --- 1. AUTO-INSTALL REQUIREMENTS ---
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
COOKIE = os.environ.get("INSTA_COOKIE")
TARGET = os.environ.get("TARGET_THREAD_ID") 
MESSAGES = os.environ.get("MESSAGES", "Hello|Hi|Bot Active").split("|")

SLIDER_LIMIT = 1000       # How many messages to send
SLIDER_DELAY = (10, 30)   # Wait 10-30s between replies
SESSION_TIME = 600        # Restart browser every 10 mins

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 {msg}", flush=True)

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=375,812")
    options.add_argument("--disable-notifications")
    
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

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
    try:
        xpath = "//button[contains(text(), 'Not Now')] | //button[contains(text(), 'Not now')] | //button[contains(text(), 'Cancel')]"
        for btn in driver.find_elements(By.XPATH, xpath):
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)
    except: pass

def get_last_message(driver):
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
    
    # Extract ID from URL if full link is provided
    if "/t/" in TARGET:
        target_id = re.search(r'/t/(\d+)', TARGET).group(1)
    else:
        target_id = re.sub(r'\D', '', TARGET)

    url = f"https://www.instagram.com/direct/t/{target_id}/"
    log(f"🎯 Target Locked: {target_id}")

    while sent_count < SLIDER_LIMIT:
        driver = None
        try:
            log("🚀 Launching Browser...")
            driver = get_driver()
            
            # --- ROBUST COOKIE INJECTION ---
            try:
                # 1. Load the real domain first
                driver.get("https://www.instagram.com/")
                
                # 2. WAIT for it to actually initialize
                time.sleep(5) 
                
                # 3. Inject Cookie
                driver.add_cookie({
                    'name': 'sessionid', 
                    'value': COOKIE, 
                    'domain': '.instagram.com', 
                    'path': '/'
                })
                
                # 4. Refresh to apply login
                driver.refresh()
                time.sleep(5)
                
            except Exception as cookie_error:
                log(f"❌ Cookie Injection Failed: {cookie_error}")
                driver.quit()
                continue # Retry the loop

            # 5. Navigate to Chat
            driver.get(url)
            time.sleep(5)
            close_popups(driver)

            # Check if login worked
            if "login" in driver.current_url:
                log("⚠️ Login Failed. Cookie might be expired.")
                break

            last_msg = get_last_message(driver)
            log(f"✅ Connected. Last msg seen: '{last_msg}'")
            
            session_start = time.time()

            # --- THE SLIDER LOOP ---
            while (time.time() - session_start) < SESSION_TIME:
                if sent_count >= SLIDER_LIMIT: break

                current_msg = get_last_message(driver)
                
                if current_msg and current_msg != last_msg:
                    log(f"📩 Incoming: {current_msg}")
                    wait_time = random.randint(*SLIDER_DELAY)
                    time.sleep(wait_time)
                    
                    reply = random.choice(MESSAGES)
                    if send_msg(driver, reply):
                        sent_count += 1
                        log(f"📤 Sent ({sent_count}/{SLIDER_LIMIT}): {reply}")
                        last_msg = reply 
                        time.sleep(2)
                        check = get_last_message(driver)
                        if check: last_msg = check
                
                time.sleep(2)

        except Exception as e:
            log(f"⚠️ Crash: {e}")
        finally:
            if driver: driver.quit()
            log("♻️ Restarting Session (Memory Cleanup)...")
            time.sleep(5)

    log("🏁 Slider Limit Reached. Bye Praveer!")

if __name__ == "__main__":
    main()
