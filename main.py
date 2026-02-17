"""
=====================================================
   🚀 INSTAGRAPI SLIDER (Proxy + Session ID)
   --------------------------------------------------
   🔥 CREDITS: Auto reply by Praveer
   --------------------------------------------------
   - Proxy: OwlProxy (USA Custom Zone)
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

# --- PROXY CONFIGURATION ---
PROXY_URL = "http://EibxO4p1dJ50_custom_zone_US_st__city_sid_87773395_time_5:2281862@change4.owlproxy.com:7778"

def log(msg):
    print(f"[🤖 BOT]: {msg}", flush=True)

def main():
    print("=========================================")
    print("   🚀 INSTAGRAPI BOT BY PRAVEER          ")
    print("=========================================")

    if not SESSION_ID or not THREAD_ID:
        log("❌ Error: Missing SESSION_ID or THREAD_ID in Secrets!")
        sys.exit(1)

    cl = Client()
    
    # 1. Set Proxy
    log("🌐 Setting up OwlProxy...")
    cl.set_proxy(PROXY_URL)

    # 2. Randomize Device (Prevents Fingerprint Bans)
    log("📱 Generating new device fingerprint...")
    cl.set_device({
        "app_version": "269.0.0.18.75",
        "android_version": random.randint(28, 33),
        "android_release": str(random.randint(9, 13)),
        "dpi": "440dpi",
        "resolution": "1080x2280",
        "manufacturer": "Samsung",
        "device": "galaxy-s21",
        "model": "SM-G991B",
        "cpu": "exynos2100",
        "version_code": "314578889"
    })

    # 3. Login via Session ID
    try:
        log("🔑 Authenticating via Session ID...")
        cl.login_by_sessionid(SESSION_ID)
        me = cl.account_info()
        log(f"✅ Success! Logged in as: {me.username}")
    except Exception as e:
        log(f"❌ Login Failed: {e}")
        log("💡 TIP: Check if your Session ID is expired or if the Proxy is active.")
        sys.exit(1)

    log(f"🎯 Monitoring Thread: {THREAD_ID}")
    last_msg_id = None

    # --- HIGH SPEED API LOOP ---
    while True:
        try:
            # Fetch the thread
            thread = cl.direct_thread(THREAD_ID)
            if not thread.messages:
                time.sleep(2)
                continue
            
            last_msg = thread.messages[0]

            # Check if it's a new message and NOT from us
            if last_msg.id != last_msg_id:
                if str(last_msg.user_id) != str(me.pk):
                    log(f"📩 New Message: {last_msg.text}")
                    last_msg_id = last_msg.id
                    
                    # Choose random reply
                    reply_text = random.choice(MESSAGES)
                    
                    # 4. SWIPE/QUOTE REPLY
                    # This quotes the user's message in the reply
                    cl.direct_answer(THREAD_ID, reply_text, replied_to_message_id=last_msg.id)
                    
                    log(f"🚀 Sent Quoted Reply: {reply_text}")
                    log("🔥 Credit: Auto reply by Praveer")
                else:
                    # Sync ID if we sent the last message
                    last_msg_id = last_msg.id

            # Poll every 2 seconds (API is faster than browser)
            time.sleep(2)

        except Exception as e:
            log(f"⚠️ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
