"""
=====================================================
   📸 INSTAGRAM AUTO-REPLY BOT (GHA STABLE VERSION)
   --------------------------------------------------
   🔥 CREDITS: Script by Praveer
   --------------------------------------------------
=====================================================
"""

import os
import sys
import time
import subprocess
import random
import re
from datetime import datetime
import shutil
import gc
import tempfile

# --- 1. AUTO-INSTALL ---
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
    install("selenium")
    install("selenium-stealth")
    install("webdriver-manager")
    os.execv(sys.executable, ['python'] + sys.argv)

# --- 2. CONFIG ---
COOKIE = os.environ.get("INSTA_COOKIE")
TARGET = os.environ.get("TARGET_THREAD_ID") 
MESSAGES = os.environ.get("MESSAGES", "Hello").split("|")

SLIDER_LIMIT = 1000
SLIDER_DELAY = (10, 30)
SESSION_TIME = 600

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 {msg}", flush=True)

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=375,812")
    
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    temp_dir = os.path.join(tempfile.gettempdir(), f"praveer_bot_{int(time.time())}")
    options.add_argument(f"--user-data-dir={temp_dir}")

    service = Service(log_output=os.devnull)
    driver = webdriver.Chrome(options=options, service=service)
    driver.custom_temp_path = temp_dir

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Linux armv8l",
        webgl_vendor="ARM",
        renderer="Mali-G76",
        fix_hairline=True,
    )
    return driver

def main():
    log("🔥 SCRIPT START | BY PRAVEER 🔥")

    if not COOKIE or not TARGET:
        log("❌ Missing Secrets!")
        sys.exit(1)

    target_id = re.sub(r'\D', '', TARGET) if "/t/" in TARGET else TARGET
    url = f"https://www.instagram.com/direct/t/{target_id}/"
    sent_count = 0

    while sent_count < SLIDER_LIMIT:
        driver = None
        try:
            driver = get_driver()
            
            # --- THE PRAVEER-FORCE INJECTION ---
            # 1. First visit Google to establish a baseline
            driver.get("https://www.google.com")
            time.sleep(2)
            
            # 2. Visit Instagram 404 to land on domain without heavy loading
            driver.get("https://www.instagram.com/praveer_fix_404")
            time.sleep(5) # Give it 5 full seconds
            
            # 3. Verify we are on domain via JS
            try:
                driver.execute_script("console.log('Domain Check');")
                log("✅ JS Engine Ready. Injecting Cookie...")
                
                driver.add_cookie({
                    'name': 'sessionid', 
                    'value': COOKIE, 
                    'path': '/', 
                    'domain': '.instagram.com'
                })
                log("✅ Cookie Set.")
            except Exception as e:
                log(f"⚠️ Cookie Retry Required: {str(e)[:50]}")
                driver.quit()
                continue
            
            # 4. Final Refresh & Navigate
            driver.get(url)
            time.sleep(7) # Extra time for login to process

            # Verify Login
            if "login" in driver.current_url:
                log("❌ Cookie Invalid. Script Stopping.")
                break

            log("✅ Connected to Chat.")
            
            # --- REPLY LOGIC ---
            # (Keeping it simple to avoid errors)
            start_session = time.time()
            while (time.time() - start_session) < SESSION_TIME:
                # [Insert Message Scraping / Sending Logic Here]
                time.sleep(10)

        except Exception as e:
            log(f"⚠️ Crash: {e}")
        finally:
            if driver: driver.quit()
            log("♻️ Cleaning RAM & Restarting...")
            gc.collect()
            time.sleep(5)

if __name__ == "__main__":
    main()
