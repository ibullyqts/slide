"""
=====================================================
   🚀 INSTAGRAPI SLIDER (SOCKS5 Edition)
   --------------------------------------------------
   🔥 CREDITS: Auto reply by Praveer
=====================================================
"""

import os
import time
import random
import sys
import requests
from instagrapi import Client

# --- INSTAGRAM CREDITS ---
INSTA_USER = "bhangilode"
INSTA_PASS = "praveer123"

# --- CONFIGURATION (GitHub Secrets) ---
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
MESSAGES = os.environ.get("MESSAGES", "Hello!|Auto-Reply by Praveer|Active ⚡").split("|")

# --- SOCKS5 PROXY DATA ---
# Replace with the specific IP and Port provided by vmoscloud
PX_HOST = "api.vmoscloud.com" 
PX_PORT = "1080" # Example SOCKS5 port
PX_USER = "7RkSZhW0WwvH4aYbCFJvMklNdwIuk2HI"
PX_PASS = "ZjJyPu1MLCbf5v7xKA1wfeiP"

# SOCKS5 Format for Instagrapi
PROXY_URL = f"socks5://{PX_USER}:{PX_PASS}@{PX_HOST}:{PX_PORT}"

def log(msg):
    print(f"[🤖 BOT]: {msg}", flush=True)

def check_socks5_connection():
    """Verify SOCKS5 tunnel is working before login"""
    try:
        # We use a standard request to check the IP via the proxy
        proxies = {'http': PROXY_URL, 'https': PROXY_URL}
        response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=20)
        ip = response.json()['ip']
        log(f"✅ SOCKS5 Connected! Proxy IP: {ip}")
        return True
    except Exception as e:
        log(f"❌ SOCKS5 Connection Failed: {e}")
        return False

def main():
    print("=========================================")
    print("   🚀 INSTAGRAPI SOCKS5 BOT BY PRAVEER   ")
    print("=========================================")

    if not THREAD_ID:
        log("❌ Error: Missing TARGET_THREAD_ID in Secrets!")
        sys.exit(1)

    # 1. Connection Check
    if not check_socks5_connection():
        log("🛑 STOPPING: SOCKS5 Proxy is not responding. Check Host/Port/Keys.")
        sys.exit(1)

    cl = Client()
    cl.set_proxy(PROXY_URL)

    # 2. Randomize Device
    cl.set_device({
        "app_version": "269.0.0.18.75",
        "android_version": 33,
        "android_release": "13.0",
        "dpi": "440dpi",
        "resolution": "1080x2280",
        "manufacturer": "Samsung",
        "device": "galaxy-s22",
        "model": "SM-S901B",
        "cpu": "exynos2200",
        "version_code": "314578889"
    })

    # 3. Login
    try:
        log(f"🔑 Logging into @{INSTA_USER}...")
        cl.login(INSTA_USER, INSTA_PASS)
        me = cl.account_info()
        log(f"✅ SUCCESS! Logged in as: {me.username}")
    except Exception as e:
        log(f"❌ Login Failed: {e}")
        sys.exit(1)

    log(f"🎯 Monitoring Thread: {THREAD_ID}")
    last_msg_id = None

    # --- MAIN LOOP ---
    while True:
        try:
            thread = cl.direct_thread(THREAD_ID)
            if not thread.messages:
                time.sleep(3)
                continue
            
            last_msg = thread.messages[0]

            if last_msg.id != last_msg_id:
                if str(last_msg.user_id) != str(me.pk):
                    log(f"📩 New Message: {last_msg.text}")
                    last_msg_id = last_msg.id
                    
                    reply_text = random.choice(MESSAGES)
                    # Quoted/Swipe Reply
                    cl.direct_answer(THREAD_ID, reply_text, replied_to_message_id=last_msg.id)
                    
                    log(f"🚀 Sent Quoted Reply: {reply_text}")
                    log("🔥 Credit: Auto reply by Praveer")
                else:
                    last_msg_id = last_msg.id

            time.sleep(2)
        except Exception as e:
            log(f"⚠️ Loop Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
