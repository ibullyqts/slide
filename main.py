"""
=====================================================
   🚀 INSTAGRAPI SLIDER (Safe Proxy & IP Check)
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

# --- CONFIGURATION ---
SESSION_ID = os.environ.get("INSTA_COOKIE")
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
MESSAGES = os.environ.get("MESSAGES", "Hello!|Auto-Reply by Praveer|Active ⚡").split("|")

# --- PROXY RAW DATA (Host:Port:User:Pass) ---
PX_HOST = "change4.owlproxy.com"
PX_PORT = "7778"
PX_USER = "EibxO4p1dJ50_custom_zone_US_st__city_sid_82468756_time_90"
PX_PASS = "2281862"

# Format for Instagrapi
PROXY_URL = f"http://{PX_USER}:{PX_PASS}@{PX_HOST}:{PX_PORT}"

def log(msg):
    print(f"[🤖 BOT]: {msg}", flush=True)

def check_ip():
    """Verify if the proxy is actually working"""
    try:
        proxies = {'http': PROXY_URL, 'https': PROXY_URL}
        response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=10)
        new_ip = response.json()['ip']
        log(f"🌐 Proxy Active! Current IP: {new_ip}")
        return True
    except Exception as e:
        log(f"❌ Proxy IP Check Failed: {e}")
        return False

def main():
    print("=========================================")
    print("   🚀 INSTAGRAPI BOT BY PRAVEER          ")
    print("=========================================")

    if not SESSION_ID or not THREAD_ID:
        log("❌ Error: Missing Secrets (INSTA_COOKIE or TARGET_THREAD_ID)!")
        sys.exit(1)

    # 1. Verify Proxy Connection first
    if not check_ip():
        log("⚠️ Proceeding without confirmed proxy (might fail)...")

    cl = Client()
    
    # 2. Set Proxy
    cl.set_proxy(PROXY_URL)

    # 3. Randomize Device
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

    # 4. Login via Session ID
    try:
        log("🔑 Attempting Login via Session ID...")
        cl.login_by_sessionid(SESSION_ID)
        me = cl.account_info()
        log(f"✅ SUCCESS! Logged in as: {me.username}")
    except Exception as e:
        log(f"❌ Login Failed: {e}")
        log("💡 Check: 1. Is the Proxy port 7778 open? 2. Is your Session ID fresh?")
        sys.exit(1)

    log(f"🎯 Monitoring Thread: {THREAD_ID}")
    last_msg_id = None

    # --- MAIN LOOP ---
    while True:
        try:
            thread = cl.direct_thread(THREAD_ID)
            if not thread.messages:
                time.sleep(2)
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
            log(f"⚠️ Error during loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
