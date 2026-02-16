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
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
THREADS = 1             
TOTAL_DURATION = 25000  
SESSION_MIN_SEC = 300   

GLOBAL_SENT = 0
COUNTER_LOCK = threading.Lock()
BROWSER_LAUNCH_LOCK = threading.Lock()

sys.stdout.reconfigure(encoding='utf-8')

def log_status(agent_id, msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Agent {agent_id}: {msg}", flush=True)

def get_driver(agent_id):
    with BROWSER_LAUNCH_LOCK:
        time.sleep(3) 
        chrome_options = Options()
        
        # 🛡️ STABILITY FLAGS
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_argument("--window-size=375,812")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        
        mobile_emulation = {
            "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        temp_dir = os.path.join(tempfile.gettempdir(), f"linux_v100_reply_{agent_id}_{int(time.time())}")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

        service = Service(log_output=os.devnull) 
        
        try:
            driver = webdriver.Chrome(options=chrome_options, service=service)
        except Exception as e:
            print(f"❌ Driver Launch Failed: {e}")
            raise e

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux armv8l", 
            webgl_vendor="ARM",
            renderer="Mali-G76",
            fix_hairline=True,
        )
        
        driver.custom_temp_path = temp_dir
        driver.set_page_load_timeout(30)
        return driver

def close_popups(driver):
    try:
        # "Not Now" buttons
        xpath = "//button[contains(text(), 'Not Now')] | //button[contains(text(), 'Not now')]"
        buttons = driver.find_elements(By.XPATH, xpath)
        for btn in buttons:
            try:
                btn.click()
                time.sleep(0.5)
            except:
                driver.execute_script("arguments[0].click();", btn)
        
        # "Cancel" buttons (Add to home screen)
        try:
            cancel = driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
            cancel.click()
        except: pass
    except: pass

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
    Scrapes the chat to find the text of the very last message.
    Scopes to <main> to avoid reading the Header/Username.
    """
    # 🚫 STATIC IGNORE LIST
    IGNORE_LIST = [
        "Not Now", "Not now", "Turn On", "Turn on", 
        "Seen", "Double tap to like", "Send", 
        "Active now", "Active today", "Save info", 
        "Save your login info"
    ]

    # 🚫 DYNAMIC IGNORE: Add the Chat Title (Target Name) to ignore list
    try:
        header_title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        if header_title: IGNORE_LIST.append(header_title)
    except: pass

    try:
        # 🎯 SCOPED SELECTOR: Only look inside <main> tag to avoid Header bar
        # This is the key fix for "ritu.zii" appearing
        elements = driver.find_elements(By.XPATH, "//main//div[contains(@role, 'row')]//div[contains(@dir, 'auto')]")
        
        # Fallback if structure is different
        if not elements:
            elements = driver.find_elements(By.XPATH, "//main//div[contains(@class, 'x')]//span")
            
        if elements:
            # Check last 5 elements
            check_range = min(len(elements), 5)
            
            for i in range(1, check_range + 1):
                try:
                    text_obj = elements[-i]
                    text = text_obj.text.strip()
                    
                    if not text: continue

                    # Filter check
                    is_ignored = False
                    for bad_word in IGNORE_LIST:
                        if bad_word in text:
                            is_ignored = True
                            break
                    
                    if not is_ignored:
                        return text
                except: continue
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
            btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Send')] | //button[text()='Send']")
            driver.execute_script("arguments[0].click();", btn)
        except:
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
            
            close_popups(driver)
            time.sleep(2)
            
            log_status(agent_id, "[LISTEN] Connected. Scoping messages...")
            
            last_seen_text = get_last_message_text(driver)
            log_status(agent_id, f"Initial state (Last Msg): '{last_seen_text[:20]}'")

            msg_box = find_mobile_box(driver)

            while (time.time() - session_start) < SESSION_MIN_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break

                if not msg_box:
                    msg_box = find_mobile_box(driver)
                    if not msg_box:
                        time.sleep(2)
                        continue

                current_text = get_last_message_text(driver)

                if current_text and current_text != last_seen_text:
                    log_status(agent_id, f"[NEW MSG] >> {current_text[:30]}")
                    time.sleep(random.uniform(2, 6))
                    
                    reply_text = random.choice(messages)
                    if adaptive_inject(driver, msg_box, f"{reply_text}"):
                        log_status(agent_id, f"[REPLY] >> {reply_text}")
                        with COUNTER_LOCK:
                            global GLOBAL_SENT
                            GLOBAL_SENT += 1
                        
                        last_seen_text = reply_text 
                        time.sleep(3) 
                        
                        actual_ui_text = get_last_message_text(driver)
                        if actual_ui_text: last_seen_text = actual_ui_text

                time.sleep(1.5)

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
    messages = os.environ.get("MESSAGES", "Hello|Hi").split("|")
    
    if len(cookie) < 5:
        sys.exit(1)

    try: subprocess.run("pkill -f chrome", shell=True)
    except: pass

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(run_life_cycle, i+1, cookie, target, messages)

if __name__ == "__main__":
    main()
