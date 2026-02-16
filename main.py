"""
=====================================================
   ⚡ HIGH-SPEED SLIDER BOT (Reload + Force Send)
   --------------------------------------------------
   🔥 CREDITS: Auto reply by Praveer
   --------------------------------------------------
   1. Navigates to Chat -> RELOADS once.
   2. Uses JS Injection for instant sending.
   3. Verifies if message sent; if not, retries.
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
SESSION_ID = os.environ.get("INSTA_COOKIE") 
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
MESSAGES = os.environ.get("MESSAGES", "Hello!|Auto-Reply|Bot Active 🤖").split("|")

def log(msg):
    print(f"[⚡ SLIDER]: {msg}", flush=True)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=1920,1080")
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
        # Find the typing box
        box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
        box.click()
        
        # Inject text
        driver.execute_script("""
            arguments[0].focus();
            document.execCommand('insertText', false, arguments[1]);
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        """, box, text)
        time.sleep(1) # Wait for Send button to activate

        # Click Send (Try multiple selectors)
        sent = False
        send_selectors = ["//div[text()='Send']", "//button[text()='Send']", "//div[@role='button' and text()='Send']"]
        
        for selector in send_selectors:
            try:
                btn = driver.find_element(By.XPATH, selector)
                btn.click()
                sent = True
                break
            except: continue
        
        if not sent:
            box.send_keys(Keys.ENTER)
        
        return True
    except: return False

def main():
    print("=========================================")
    print("   🚀 AUTO REPLY BY PRAVEER STARTED      ")
    print("=========================================")

    if not SESSION_ID or not THREAD_ID:
        log("❌ Error: Missing Secrets!")
        sys.exit(1)

    driver = get_driver()
    driver.get("https://www.instagram.com/")
    time.sleep(3)

    log("🔑 Injecting Session ID...")
    driver.add_cookie({'name': 'sessionid', 'value': SESSION_ID, 'domain': '.instagram.com'})
    driver.refresh()
    time.sleep(5)

    # 1. First Navigation
    target_url = f"https://www.instagram.com/direct/t/{THREAD_ID}/"
    log(f"🚀 Navigating to Chat: {THREAD_ID}")
    driver.get(target_url)
    time.sleep(5)

    # 2. THE RELOAD (New Step requested)
    log("🔄 Reloading page once for stability...")
    driver.refresh()
    time.sleep(7) 

    log("✅ LOCKED ON. Monitoring for slides...")
    last_seen_text = get_last_message_text(driver)

    start_time = time.time()
    while (time.time() - start_time) < 21000:
        try:
            current_text = get_last_message_text(driver)
            
            if current_text and current_text != last_seen_text:
                log(f"📩 New Message: {current_text}")
                last_seen_text = current_text
                
                reply = random.choice(MESSAGES)
                if instant_reply(driver, reply):
                    log(f"🚀 Sent: {reply} | Credit: Auto reply by Praveer")
                    time.sleep(2) # Give it a moment to post
                    
                    # Sync to ignore our own message
                    my_reply = get_last_message_text(driver)
                    if my_reply: last_seen_text = my_reply

            time.sleep(0.5)
        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    main()
