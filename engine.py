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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
THREADS = 1             # Keep at 1 for reply logic
TOTAL_DURATION = 25000  # Total run time (seconds)
SESSION_MIN_SEC = 300   # Restart browser every 5 minutes (to clear RAM)

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()
BROWSER_LAUNCH_LOCK = threading.Lock()

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    with BROWSER_LAUNCH_LOCK:
        time.sleep(2) 
        chrome_options = Options()
        
        # 🐧 LINUX / SERVER OPTIMIZATIONS
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox") 
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--renderer-process-limit=2")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        
        # MOBILE EMULATION (iPhone X Mode - Crucial for this layout)
        mobile_emulation = {
            "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        temp_dir = os.path.join(tempfile.gettempdir(), f"linux_v100_reply_{int(time.time())}_{agent_id}")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

        driver = webdriver.Chrome(options=chrome_options)

        # 🪄 APPLY STEALTH
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux armv8l", 
            webgl_vendor="ARM",
            renderer="Mali-G76",
            fix_hairline=True,
        )
        
        driver.custom_temp_path = temp_dir
        return driver

def close_popups(driver):
    """
    Closes 'Turn on Notifications' or 'Save Info' popups
    """
    try:
        # Look for "Not Now" buttons
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')] | //button[contains(text(), 'Not now')]")
        if buttons:
            for btn in buttons:
                try: 
                    btn.click()
                    time.sleep(1)
                except: pass
    except:
        pass

def find_mobile_box(driver):
    selectors = ["//textarea", "//div[@role='textbox']", "//div[contains(@contenteditable, 'true')]"]
    for xpath in selectors:
        try: 
            el = driver.find_element(By.XPATH, xpath)
            return el
        except: continue
    return None

def get_last_message_text(driver):
    """
    Scrapes the chat to find the text of the very last message bubble.
    Ignores system text like 'Seen', 'Today', etc.
    """
    try:
        # Broad selector for message bubbles in mobile view
        elements = driver.find_elements(By.XPATH, "//div[contains(@role, 'row')]//div[contains(@dir, 'auto')]")
        
        if not elements:
            # Fallback for different DOM structures
            elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'x')]//span")
            
        if elements:
            text = elements[-1].text.strip()
            # Filter out common UI noise if the popup click failed
            if text in ["Not Now", "Turn On", "Seen", "Double tap to like"]:
                return ""
            return text
    except:
        pass
    return ""

def adaptive_inject(driver, element, text):
    try:
        driver.execute_script("arguments[0].click();", element)
        driver.execute_script("""
            var el = arguments[0];
            document.execCommand('insertText', false, arguments[1]);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, element, text)
        
        time.sleep(0.5)
        try:
            # Try clicking generic Send button
            btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']")
            driver.execute_script("arguments[0].click();", btn)
        except:
            # Fallback to Enter key
            element.send_keys(Keys.ENTER)
        return True
    except:
        return False

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
            
            driver.get("https://www.instagram.com/")
            time.sleep(2) 

            clean_session = extract_session_id(cookie)
            driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'path': '/', 'domain': '.instagram.com'})
            driver.refresh()
            time.sleep(random.uniform(3, 5)) 
            
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(5) 
            
            # --- CRITICAL FIX: CLOSE POPUPS ---
            close_popups(driver)
            time.sleep(2)
            
            log_status(agent_id, "[LISTEN] Connected to chat. Waiting for new messages...")
            
            # 1. Take a snapshot of the current last message
            last_seen_text = get_last_message_text(driver)
            log_status(agent_id, f"Initial state: '{last_seen_text[:20]}'")

            msg_box = find_mobile_box(driver)

            while (time.time() - session_start) < SESSION_MIN_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break

                # Refresh the msg box element if it goes stale
                if not msg_box:
                    msg_box = find_mobile_box(driver)
                    if not msg_box:
                        time.sleep(2)
                        continue

                # 2. Check current last message
                current_text = get_last_message_text(driver)

                # 3. If the text has CHANGED, it means a new message arrived
                if current_text and current_text != last_seen_text:
                    
                    log_status(agent_id, f"[NEW MSG] >> {current_text[:30]}")
                    
                    # Wait a random time to simulate reading/typing
                    time.sleep(random.uniform(2, 6))
                    
                    # 4. Pick a reply and send
                    reply_text = random.choice(messages)
                    
                    if adaptive_inject(driver, msg_box, f"{reply_text}"):
                        log_status(agent_id, f"[REPLY] >> {reply_text}")
                        with COUNTER_LOCK:
                            global GLOBAL_SENT
                            GLOBAL_SENT += 1
                        
                        # 5. Update last_seen_text to what WE just sent
                        # This ensures we don't reply to ourselves
                        last_seen_text = reply_text 
                        
                        # Wait for UI update
                        time.sleep(3) 
                        
                        # Verify UI state
                        actual_ui_text = get_last_message_text(driver)
                        if actual_ui_text:
                            last_seen_text = actual_ui_text

                time.sleep(1.5) # Check loop frequency

        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            log_status(agent_id, f"[ERROR] {err_msg[:50]}...")
        
        finally:
            log_status(agent_id, "[CLEAN] ♻️ Restarting Session...")
            if driver: 
                try: driver.quit()
                except: pass
            
            if temp_path and os.path.exists(temp_path):
                try: shutil.rmtree(temp_path, ignore_errors=True)
                except: pass
            
            gc.collect() 
            time.sleep(3) 

def main():
    cookie = os.environ.get("INSTA_COOKIE", "").strip()
    target = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello|Hi|What's up").split("|")
    
    if len(cookie) < 5:
        print("Error: INSTA_COOKIE not found.")
        sys.exit(1)

    try: subprocess.run("pkill -f chrome", shell=True)
    except: pass

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()
