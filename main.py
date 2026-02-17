"""
=====================================================
   🚀 INSTAGRAPI SLIDER (ID & Password Login)
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

# --- CONFIGURATION ---
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
MESSAGES = os.environ.get("MESSAGES", "Hello!|Auto-Reply by Praveer|Active ⚡").split("|")

# --- PROXY DATA (Host:Port:User:Pass) ---
PX_HOST = "change4.owlproxy.com"
PX_PORT = "7778"
PX_USER = "EibxO4p1dJ50_custom_zone_US_st__city_sid_82468756_time_90"
PX_PASS = "2281862"

# Instagrapi format
PROXY_URL = f"http://{PX_USER}:{PX_PASS}@{PX_HOST}:{PX_PORT}"

def log(msg):
    print(f"[🤖 BOT]: {msg}", flush=True)

def check_ip():
    """Verify proxy tunnel is open before sending credentials"""
    try:
        proxies = {'http': PROXY_URL, 'https': PROXY_URL}
        response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=15)
        new_ip = response.json()['ip']
        log(f"🌐 Proxy Tunnel Established. IP: {new_ip}")
        return True
    except Exception as e:
        log(f"❌ Proxy Authentication Failed: {e}")
        return False

def main():
    print("=========================================")
    print("   🚀 INSTAGRAPI BOT BY PRAVEER          ")
    print("=========================================")

    if not THREAD_ID:
        log("❌ Error: Missing TARGET_THREAD_ID in GitHub Secrets!")
        sys.exit(1)

    # 1. Verify Proxy first (Safety check)
    if not check_ip():
        log("🛑 STOPPING: Connection is not secure. Check your Proxy details.")
        sys.exit(1)

    cl = Client()
    cl.set_proxy(PROXY_URL)

    # 2. Randomize Device Fingerprint
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

    # 3. Login via Username/Password
    try:
        log(f"🔑 Attempting Login for @{INSTA_USER}...")
        cl.login(INSTA_USER, INSTA_PASS)
        me = cl.account_info()
        log(f"✅ SUCCESS! Logged in as: {me.username}")
    except Exception as e:
        log(f"❌ Login Failed: {e}")
        log("💡 Check: Is Two-Factor Authentication (2FA) off? Is the password correct?")
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

            # If NEW message and NOT from me
            if last_msg.id != last_msg_id:
                if str(last_msg.user_id) != str(me.pk):
                    log(f"📩 New Message: {last_msg.text}")
                    last_msg_id = last_msg.id
                    
                    reply_text = random.choice(MESSAGES)
                    # Quoted Reply (Like a Swipe)
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
