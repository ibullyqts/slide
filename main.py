"""
=====================================================
   🚀 INSTAGRAM API BOT (Instagrapi Version)
   --------------------------------------------------
   🔥 CREDITS: Script by Praveer
   --------------------------------------------------
   FEATURES:
   - Uses Official-like API (No Chrome/Selenium)
   - Auto-Reply Slider Logic (Ping-Pong)
   - "Typing..." Status Simulation
   - zero-crash stability for GitHub Actions
=====================================================
"""

import os
import sys
import time
import random
import subprocess
from datetime import datetime

# --- 1. AUTO-INSTALL INSTAGRAPI ---
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from instagrapi import Client
except ImportError:
    print("📦 Installing Instagrapi...")
    install("instagrapi")
    print("✅ Installed! Restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)

# --- 2. CONFIGURATION ---
# Secrets from GitHub/Env
SESSION_ID = os.environ.get("INSTA_COOKIE") # Your 'sessionid' cookie value
THREAD_ID = os.environ.get("TARGET_THREAD_ID") # e.g. 887427387249300
MESSAGES = os.environ.get("MESSAGES", "Hello|Hi|I am active").split("|")

# Slider Settings
POLL_INTERVAL = (5, 10)     # Check for new msg every 5-10s
REPLY_DELAY = (2, 5)        # Wait 2-5s before sending reply (Humanize)
TOTAL_RUN_TIME = 21000      # 6 Hours (Safe for GitHub Actions)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 {msg}", flush=True)

def main():
    log("🔥 INSTAGRAPI BOT STARTED | BY PRAVEER 🔥")

    if not SESSION_ID or not THREAD_ID:
        log("❌ Error: Missing INSTA_COOKIE or TARGET_THREAD_ID")
        sys.exit(1)

    # Clean Thread ID
    t_id = THREAD_ID.split("/")[-2] if "instagram.com" in THREAD_ID else THREAD_ID
    
    cl = Client()
    
    # --- LOGIN ---
    try:
        log("🔑 Logging in via Session ID...")
        cl.login_by_sessionid(SESSION_ID)
        me = cl.account_info()
        my_id = me.pk
        log(f"✅ Logged in as: {me.username} ({my_id})")
    except Exception as e:
        log(f"❌ Login Failed: {e}")
        sys.exit(1)

    # --- SLIDER LOOP ---
    start_time = time.time()
    last_msg_id = None
    
    log(f"🎯 Locked on Thread: {t_id}")
    log("👂 Listening for new messages...")

    while (time.time() - start_time) < TOTAL_RUN_TIME:
        try:
            # 1. Fetch the specific thread
            thread = cl.direct_thread(t_id)
            
            # 2. Get the very last message
            if not thread.messages:
                time.sleep(5)
                continue
                
            last_msg = thread.messages[0] # Index 0 is the newest message
            
            # 3. Check if it's new AND not from us (The "Slide" Logic)
            if last_msg.id != last_msg_id:
                
                # Check if sender is NOT me
                if str(last_msg.user_id) != str(my_id):
                    log(f"📩 Incoming: {last_msg.text}")
                    
                    # Update state immediately so we don't double-reply
                    last_msg_id = last_msg.id
                    
                    # Human Delay
                    delay = random.randint(*REPLY_DELAY)
                    time.sleep(delay)
                    
                    # 4. Simulate Action (Mark seen + Typing)
                    log("👀 Marking Seen...")
                    cl.direct_seen(t_id, [last_msg.id])
                    cl.direct_send_seen(t_id)
                    
                    # 5. Send Reply
                    reply_text = random.choice(MESSAGES)
                    log(f"📤 Sending: {reply_text}")
                    cl.direct_answer(t_id, last_msg.item_id, reply_text)
                    log("✅ Sent!")

                else:
                    # It's our own message, just update ID and wait
                    if last_msg_id != last_msg.id:
                        log(f"👤 (Self-Message detected: {last_msg.text})")
                        last_msg_id = last_msg.id

            # Sleep before next poll
            time.sleep(random.randint(*POLL_INTERVAL))

        except Exception as e:
            log(f"⚠️ API Glitch: {e}")
            time.sleep(10) # Cool down on error

    log("🏁 Time Limit Reached. Bye!")

if __name__ == "__main__":
    main()
