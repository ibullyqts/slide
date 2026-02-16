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

        # --- ACTIVATION PING ---
        # This part sends a message immediately upon connection
        ping_text = "Slider by Praveer is now Active! 🚀"
        ping_script = """
        var box = document.querySelector('textarea, [role="textbox"], div[contenteditable="true"]');
        if (box) {
            box.focus();
            document.execCommand('insertText', false, arguments[0]);
            var sendBtn = Array.from(document.querySelectorAll('button, div[role="button"]')).find(b => 
                b.innerText.includes('Send') || b.getAttribute('aria-label') === 'Send'
            );
            if (sendBtn) sendBtn.click();
            return true;
        }
        return false;
        """
        if driver.execute_script(ping_script, ping_text):
            log("📡 Activation Ping Sent!")
        else:
            log("⚠️ Failed to send Activation Ping. Box not found.")

        # --- AUTO-REPLY LISTENER ---
        script = """
        window.lastCount = document.querySelectorAll('div[role="row"]').length;
        window.msgs = arguments[0];
        
        setInterval(() => {
            let rows = document.querySelectorAll('div[role="row"]');
            if (rows.length > window.lastCount) {
                console.log("BOT_SIGNAL: NEW_MESSAGE_DETECTED");
                window.lastCount = rows.length;
                let lastRow = rows[rows.length - 1];

                if (!lastRow.innerText.includes('You sent') && !lastRow.innerText.includes('Slider by Praveer')) {
                    let replyBtn = lastRow.querySelector('button[aria-label="Reply"]') || 
                                   lastRow.querySelector('svg[aria-label="Reply"]')?.closest('button');

                    if (replyBtn) {
                        replyBtn.click();
                        console.log("BOT_SIGNAL: REPLY_CLICKED");
                        
                        setTimeout(() => {
                            let box = document.querySelector('textarea, [role="textbox"], div[contenteditable="true"]');
                            if (box) {
                                box.focus();
                                let txt = window.msgs[Math.floor(Math.random() * window.msgs.length)];
                                document.execCommand('insertText', false, txt);
                                
                                let sendBtn = Array.from(document.querySelectorAll('button, div[role="button"]')).find(b => 
                                    b.innerText.includes('Send') || b.getAttribute('aria-label') === 'Send'
                                );
                                
                                if (sendBtn) {
                                    sendBtn.click();
                                    console.log("BOT_SIGNAL: SENT_SUCCESS");
                                }
                            }
                        }, 500);
                    }
                }
            }
        }, 1000);
        """
        driver.execute_script(script, MESSAGES)
        log("✅ SLIDER ACTIVE. Monitoring for messages...")
        
        # Monitor logs
        start_time = time.time()
        while time.time() - start_time < 18000:
            for entry in driver.get_log('browser'):
                if "BOT_SIGNAL" in entry['message']:
                    msg_type = entry['message'].split("BOT_SIGNAL: ")[1].replace('"', '')
                    log(f"⚡ ACTION: {msg_type}")
            time.sleep(2)
        
    except Exception as e:
        log(f"⚠️ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if not RAW_COOKIE or not TARGET_ID:
        log("❌ Error: Secrets not found!")
        sys.exit(1)
    start_engine()
