"""
=====================================================
   🚀 INSTAGRAPI SLIDER (Host:Port:User:Pass Format)
   --------------------------------------------------
   🔥 CREDITS: Auto reply by Praveer
   --------------------------------------------------
   - Proxy: OwlProxy (IP Authentication Fixed)
   - Method: Quoted/Swipe Reply
   - Platform: GitHub Actions
=====================================================
"""

import os
import time
import random
import sys
from instagrapi import Client

# --- CONFIGURATION (GitHub Secrets) ---
SESSION_ID = os.environ.get("INSTA_COOKIE")
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
MESSAGES = os.environ.get("MESSAGES", "Hello!|Auto-Reply by Praveer|Active ⚡").split("|")

# --- PROXY SETTINGS (Host:Port:User:Pass) ---
PX_HOST = "change4.owlproxy.com"
PX_PORT = "7778"
PX_USER = "EibxO4p1dJ50_custom_zone_US_st__city_sid_87773395_time_5"
PX_PASS = "2281862"

# Constructing the URL for instagrapi
PROXY_URL = f"http://{PX_USER}:{PX_PASS}@{PX_HOST}:{PX_PORT}"

def log(msg):
    print(f"[🤖 BOT]: {msg}", flush=True)

def main():
    print("=========================================")
    print("   🚀 INSTAGRAPI BOT BY PRAVEER          ")
    print("=========================================")

    if not SESSION_ID or not THREAD_ID:
        log("❌ Error: Missing Secrets in GitHub!")
        sys.exit(1)

    cl = Client()
    
    # 1. Set Proxy
    try:
        log(f"🌐 Connecting to Proxy: {PX_HOST}...")
        cl.set_proxy(PROXY_URL)
    except Exception as e:
        log(f"❌ Proxy Connection Failed: {e}")

    # 2. Randomize Device (Essential for API)
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

    # 3. Login via Session ID
    try:
        log("🔑 Authenticating with Session ID...")
        cl.login_by_sessionid(SESSION_ID)
        me = cl.account_info()
        log(f"✅ SUCCESS! Logged in as: {me.username}")
    except Exception as e:
        log(f"❌ Login Failed: {e}")
        sys.exit(1)

    log(f"🎯 Monitoring Thread: {THREAD_ID}")
    last_msg_id = None

    # --- HIGH SPEED API LOOP ---
    while True:
        try:
            # Get latest messages from the thread
            thread = cl.direct_thread(THREAD_ID)
            if not thread.messages:
                time.sleep(2)
                continue
            
            last_msg = thread.messages[0]

            # Logic: If message is NEW and NOT sent by me
            if last_msg.id != last_msg_id:
                if str(last_msg.user_id) != str(me.pk):
                    log(f"📩 New Message: {last_msg.text}")
                    last_msg_id = last_msg.id
                    
                    # Swipe/Quote Reply logic
                    reply_text = random.choice(MESSAGES)
                    cl.direct_answer(THREAD_ID, reply_text, replied_to_message_id=last_msg.id)
                    
                    log(f"🚀 Sent Quoted Reply: {reply_text}")
                    log("🔥 Credit: Auto reply by Praveer")
                else:
                    # Avoid replying to ourselves
                    last_msg_id = last_msg.id

            # Fast polling for slider effect
            time.sleep(1.5)

        except Exception as e:
            log(f"⚠️ API Glitch: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
