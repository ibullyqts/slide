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

        # --- THE RE-ENGINEERED FORCE-SEND & OBSERVER ---
        script = """
        window.msgs = arguments[0];
        
        window.forceSend = function(text) {
            let box = document.querySelector('textarea, [role="textbox"], div[contenteditable="true"]');
            if (!box) return false;
            box.focus();
            document.execCommand('insertText', false, text);
            box.dispatchEvent(new Event('input', { bubbles: true }));
            
            setTimeout(() => {
                let sendBtn = Array.from(document.querySelectorAll('button, div[role="button"]')).find(b => 
                    b.innerText.includes('Send') || b.getAttribute('aria-label') === 'Send' || b.querySelector('svg[aria-label="Send"]')
                );
                if (sendBtn) sendBtn.click();
            }, 300);
            return true;
        };

        // 1. Send Activation Ping
        window.forceSend("Slider by Praveer is now Active! 🚀");

        // 2. Setup Mutation Observer (The Unbreakable Listener)
        const chatContainer = document.querySelector('div[role="main"]') || document.body;
        
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    let rows = document.querySelectorAll('div[role="row"]');
                    let lastRow = rows[rows.length - 1];

                    if (lastRow && !lastRow.innerText.includes('You sent') && !lastRow.dataset.replied) {
                        console.log("BOT_SIGNAL: NEW_MESSAGE_DETECTED");
                        
                        // Mark as replied so we don't spam the same message
                        lastRow.dataset.replied = "true";

                        let replyBtn = lastRow.querySelector('button[aria-label="Reply"]') || 
                                       lastRow.querySelector('svg[aria-label="Reply"]')?.closest('button');

                        if (replyBtn) {
                            replyBtn.click();
                            console.log("BOT_SIGNAL: REPLY_CLICKED");
                            
                            setTimeout(() => {
                                let txt = window.msgs[Math.floor(Math.random() * window.msgs.length)];
                                if (window.forceSend(txt)) {
                                    console.log("BOT_SIGNAL: SENT_SUCCESS");
                                }
                            }, 500);
                        }
                    }
                }
            });
        });

        observer.observe(chatContainer, { childList: true, subtree: true });
        console.log("BOT_SIGNAL: OBSERVER_ATTACHED");
        """
        driver.execute_script(script, MESSAGES)
        log("✅ SLIDER ACTIVE. MutationObserver attached.")
        
        # Monitor logs for 5 hours
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
    start_engine()
