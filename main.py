import os
import time
import re
import random
import datetime
import threading
import sys
import gc
import tempfile
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor

# 📦 STANDARD SELENIUM + STEALTH
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---
THREADS = 1             # Recommend 1 for reply logic to prevent double-replies
TOTAL_DURATION = 25000  
SESSION_MIN_SEC = 300   # 5 Minute cycles for stability
GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()
BROWSER_LAUNCH_LOCK = threading.Lock()

sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    with BROWSER_LAUNCH_LOCK:
        time.sleep(2) 
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--renderer-process-limit=2")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        
        mobile_emulation = {
            "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        temp_dir = os.path.join(tempfile.gettempdir(), f"praveer_slide_{int(time.time())}_{agent_id}")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

        driver = webdriver.Chrome(options=chrome_options)
        stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Linux armv8l", webgl_vendor="ARM", renderer="Mali-G76", fix_hairline=True)
        driver.custom_temp_path = temp_dir
        return driver

def find_mobile_box(driver):
    selectors = ["//textarea", "//div[@role='textbox']", "//div[contains(@contenteditable, 'true')]"]
    for xpath in selectors:
        try: 
            return driver.find_element(By.XPATH, xpath)
        except: continue
    return None

def get_last_message_text(driver):
    """Scrapes the last visible text in the chat area, ignoring system popups."""
    IGNORE = ["Not Now", "Seen", "Active", "Save info", "Double tap"]
    try:
        # We look inside the <main> tag to avoid header/ID names like 'ritu.zii'
        elements = driver.find_elements(By.XPATH, "//main//div[contains(@role, 'row')]//div[contains(@dir, 'auto')]")
        if not elements:
            elements = driver.find_elements(By.XPATH, "//main//div[contains(@class, 'x')]//span")
            
        if elements:
            for i in range(1, 6): # Check last 5 elements
                text = elements[-i].text.strip()
                if text and not any(bad in text for bad in IGNORE):
                    return text
    except: pass
    return ""

def adaptive_inject(driver, element, text):
    try:
        driver.execute_script("arguments[0].click();", element)
        driver.execute_script("var el = arguments[0]; document.execCommand('insertText', false, arguments[1]); el.dispatchEvent(new Event('input', { bubbles: true }));", element, text)
        time.sleep(0.5)
        try:
            btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']")
            driver.execute_script("arguments[0].click();", btn)
        except:
            element.send_keys(Keys.ENTER)
        return True
    except: return False

def extract_session_id(raw_cookie):
    match = re.search(r'sessionid=([^;]+)', raw_cookie)
    return match.group(1).strip() if match else raw_cookie.strip()

def run_life_cycle(agent_id, cookie, target, messages):
    global_start = time.time()

    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        temp_path = None
        session_start = time.time()
        
        try:
            log_status(agent_id, "[START] Launching Browser...")
            driver = get_driver(agent_id)
            temp_path = getattr(driver, 'custom_temp_path', None)
            
            driver.get("https://www.google.com")
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3) 

            # Domain Verification Gatekeeper
            if "instagram.com" in driver.current_url:
                driver.add_cookie({'name': 'sessionid', 'value': extract_session_id(cookie), 'path': '/', 'domain': '.instagram.com'})
                driver.refresh()
                time.sleep(5)
            
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(5)
            
            # --- CONTINUOUS SLIDE REPLY LOGIC ---
            log_status(agent_id, "[LISTEN] Monitoring Chat...")
            last_seen = get_last_message_text(driver)
            log_status(agent_id, f"Initial state: '{last_seen[:20]}'")

            while (time.time() - session_start) < SESSION_MIN_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break

                msg_box = find_mobile_box(driver)
                if not msg_box:
                    time.sleep(2)
                    continue

                current_text = get_last_message_text(driver)

                # If the text has changed, it's a new "slide" event
                if current_text and current_text != last_seen:
                    log_status(agent_id, f"[SLIDE] New message: {current_text[:30]}")
                    
                    # Human-like delay
                    time.sleep(random.uniform(2, 5))
                    
                    reply = random.choice(messages)
                    if adaptive_inject(driver, msg_box, f"{reply}"):
                        log_status(agent_id, f"[REPLY] >> {reply}")
                        with COUNTER_LOCK:
                            global GLOBAL_SENT
                            GLOBAL_SENT += 1
                        
                        # Update state to our reply so we don't reply to ourselves
                        last_seen = reply
                        time.sleep(3)
                        # Re-verify UI state
                        verify = get_last_message_text(driver)
                        if verify: last_seen = verify

                time.sleep(1.5) # Check frequency

        except Exception as e:
            log_status(agent_id, f"[ERROR] {str(e)[:50]}...")
        finally:
            log_status(agent_id, "[CLEAN] ♻️ Restarting Session...")
            if driver: driver.quit()
            if temp_path and os.path.exists(temp_path): shutil.rmtree(temp_path, ignore_errors=True)
            gc.collect()
            time.sleep(3)

def main():
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello|Hi|What's up").split("|")
    
    if len(cookie) < 5:
        sys.exit(1)

    try: subprocess.run("pkill -f chrome", shell=True)
    except: pass

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()
