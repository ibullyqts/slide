"""
=====================================================
   🚀 INSTAGRAPI DYNAMIC SLIDER (Free Credit Mode)
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

# --- DYNAMIC PROXY DATA (Host:Port:User:Pass) ---
# NOTE: For VMOS dynamic IPs, use the 'Gateway' host provided in your panel.
# If 'change4.owlproxy.com' was the host given for dynamic, keep it.
PX_HOST = "change4.owlproxy.com" 
PX_PORT = "7778" 
PX_USER = "EibxO4p1dJ50_custom_zone_US_st__city_sid_82468756_time_90"
PX_PASS = "2281862"

# SOCKS5 is best for dynamic residential credits
PROXY_URL = f"socks5://{PX_USER}:{PX_PASS}@{PX_HOST}:{PX_PORT}"

def log(msg):
    print(f"[🤖 BOT]: {msg}", flush=True)

def check_dynamic_ip():
    """Checks the current IP assigned to your dynamic credit"""
    try:
        proxies = {'http': PROXY_URL, 'https': PROXY_URL}
        # Dynamic IPs can take a few seconds to 'handshake'
        response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=30)
        ip = response.json()['ip']
        log(f"✅ Dynamic IP Active: {ip}")
        return True
    except Exception as e:
        log(f"❌ Dynamic IP Failed: {e}")
        log("💡 TIP: Check your VMOS dashboard to see if your 200MB credit is still active.")
        return False

def main():
    print("=========================================")
    print("   🚀 INSTAGRAPI DYNAMIC BOT BY PRAVEER  ")
    print("=========================================")

    if not THREAD_ID:
        log("❌ Error: Missing TARGET_THREAD_ID!")
        sys.exit(1)

    # 1. Check if dynamic credit is working
    if not check_dynamic_ip():
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
        log(f"✅ SUCCESS! Connected as: {me.username}")
    except Exception as e:
        log(f"❌ Login Failed: {e}")
        sys.exit(1)

    log(f"🎯 Monitoring Thread: {THREAD_ID}")
    last_msg_id = None

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
                    cl.direct_answer(THREAD_ID, reply_text, replied_to_message_id=last_msg.id)
                    log(f"🚀 Sent: {reply_text} | Credit: Praveer")
                else:
                    last_msg_id = last_msg.id

            time.sleep(2)
        except Exception as e:
            log(f"⚠️ API Glitch (Likely IP Rotating): {e}")
            time.sleep(10) # Wait for a fresh IP if rotation causes a glitch

if __name__ == "__main__":
    main()
