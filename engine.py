import os
import time
import random
import datetime
import sys
import gc
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
RAW_COOKIE = os.environ.get("INSTA_COOKIE")
TARGET_ID = os.environ.get("TARGET_ID")
MESSAGES = os.environ.get("REPLY_TEXTS", "🔥").split("|")

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    mobile = {"deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0}, 
              "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"}
    options.add_experimental_option("mobileEmulation", mobile)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="iPhone", fix_hairline=True)
    return driver

def start_engine():
    # --- CUSTOM CREDIT ---
    print("\n" + "="*30)
    print("   🚀 SLIDER BY PRAVEER 🚀   ")
    print("="*30 + "\n")
    
    driver = get_driver()
    try:
        log("🔄 Initializing Stealth Engine...")
        driver.get("https://www.instagram.com/robots.txt")
        
        for item in RAW_COOKIE.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                driver.add_cookie({'name': name, 'value': value, 'domain': '.instagram.com', 'path': '/'})
        
        log(f"🔗 Connecting to Thread: {TARGET_ID}")
        driver.get(f"https://www.instagram.com/direct/t/{TARGET_ID}/")
        time.sleep(15)

        script = """
        window.lastCount = document.querySelectorAll('div[role="row"]').length;
        window.msgs = arguments[0];
        setInterval(() => {
            let rows = document.querySelectorAll('div[role="row"]');
            if (rows.length > window.lastCount) {
                window.lastCount = rows.length;
                let lastRow = rows[rows.length - 1];
                if (!lastRow.innerText.includes('You sent')) {
                    let replyBtn = lastRow.querySelector('button[aria-label="Reply"], svg[aria-label="Reply"]')?.closest('button');
                    if (replyBtn) {
                        replyBtn.click();
                        setTimeout(() => {
                            let box = document.querySelector('textarea, [role="textbox"]');
                            if (box) {
                                box.focus();
                                let txt = window.msgs[Math.floor(Math.random() * window.msgs.length)];
                                document.execCommand('insertText', false, txt);
                                let send = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Send') || b.getAttribute('aria-label') === 'Send');
                                if (send) send.click();
                            }
                        }, 300);
                    }
                }
            }
        }, 1000);
        """
        driver.execute_script(script, MESSAGES)
        log("✅ SLIDER ACTIVE. Monitoring incoming messages...")
        time.sleep(18000) 
    except Exception as e:
        log(f"⚠️ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if not RAW_COOKIE or not TARGET_ID:
        log("❌ Error: Secrets not found!")
        sys.exit(1)
    start_engine()
