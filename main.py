"""
=====================================================
   ⚡ HIGH-SPEED SLIDER BOT (No Delays)
   --------------------------------------------------
   🔥 CREDITS: Auto reply by Praveer
   --------------------------------------------------
   1. Checks for messages every 0.2 seconds.
   2. Replies via Session ID (Bypasses login blocks).
   3. Uses JS Injection for instant sending.
   4. Optimized for GitHub Actions (Headless).
=====================================================
"""

import os
import time
import random
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
# These are pulled from GitHub Secrets for safety
SESSION_ID = os.environ.get("INSTA_COOKIE") 
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
MESSAGES = os.environ.get("MESSAGES", "Hello!|Auto-Reply|Bot Active 🤖").split("|")

def log(msg):
    print(f"[⚡ SLIDER]: {msg}", flush=True)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Required for GitHub Actions
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Anti-Detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_last_message_text(driver):
    try:
        elements = driver.find_elements(By.XPATH, "//div[@role='row']//div[contains(@dir, 'auto')]")
        if not elements:
            elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'x')]//div[contains(@dir, 'auto')]")
        if elements:
            text = elements[-1].text.strip()
            if text and text not in ["Message...", "Double tap to like", "Seen"]:
                return text
    except: pass
    return ""

def instant_reply(driver, text):
    try:
        box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
        box.click()
        driver.execute_script("""
            arguments[0].focus();
            document.execCommand('insertText', false, arguments[1]);
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, box, text)
        time.sleep(0.5)
        try:
            driver.find_element(By.XPATH, "//div[text()='Send']").click()
        except:
            box.send_keys(Keys.ENTER)
        return True
    except: return False

def main():
    print("=========================================")
    print("   🚀 AUTO REPLY BY PRAVEER STARTED      ")
    print("=========================================")

    if not SESSION_ID or not THREAD_ID:
        log("❌ Error: Missing SESSION_ID or THREAD_ID in Secrets!")
        sys.exit(1)

    driver = get_driver()
    
    # 1. Open Instagram to set domain
    driver.get("https://www.instagram.com/")
    time.sleep(3)

    # 2. Inject Session ID
    log("🔑 Injecting Session ID...")
    driver.add_cookie({'name': 'sessionid', 'value': SESSION_ID, 'domain': '.instagram.com'})
    driver.refresh()
    time.sleep(5)

    # 3. Go to Thread
    target_url = f"https://www.instagram.com/direct/t/{THREAD_ID}/"
    log(f"🚀 Navigating to Chat: {THREAD_ID}")
    driver.get(target_url)
    time.sleep(5)

    log("✅ LOCKED ON. Monitoring for slides...")
    last_seen_text = get_last_message_text(driver)

    # --- HIGH SPEED LOOP ---
    start_time = time.time()
    while (time.time() - start_time) < 21000: # Run for ~6 hours
        try:
            current_text = get_last_message_text(driver)
            
            if current_text and current_text != last_seen_text:
                log(f"📩 New Message: {current_text}")
                last_seen_text = current_text
                
                reply = random.choice(MESSAGES)
                if instant_reply(driver, reply):
                    log(f"🚀 Sent: {reply} | Credit: Auto reply by Praveer")
                    time.sleep(1)
                    # Re-sync to ignore own reply
                    my_reply = get_last_message_text(driver)
                    if my_reply: last_seen_text = my_reply

            time.sleep(0.2)
        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    main()
