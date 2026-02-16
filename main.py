def run_life_cycle(agent_id, cookie, target, messages):
    global_start = time.time()

    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        temp_path = None
        session_start = time.time()
        
        try:
            log_status(agent_id, "[START] Launching Browser...")
            driver = get_driver(agent_id)
            temp_path = getattr(driver, 'custom_temp_path', None)
            
            # --- UPDATED LOGIN LOGIC ---
            # 1. Visit Instagram direct login page (Better for setting domain context)
            driver.get("https://www.instagram.com/accounts/login/")
            
            # 2. WAIT for the domain to actually be recognized by the browser
            # This kills the "invalid cookie domain" error
            domain_verified = False
            for _ in range(15):
                if "instagram.com" in driver.current_url:
                    domain_verified = True
                    break
                time.sleep(1)

            if not domain_verified:
                log_status(agent_id, "[ERROR] Domain Timeout")
                driver.quit()
                continue

            # 3. Inject Cookie (Cleaned session_id only)
            clean_session = extract_session_id(cookie)
            try:
                driver.add_cookie({
                    'name': 'sessionid', 
                    'value': clean_session, 
                    'path': '/', 
                    'domain': '.instagram.com'
                })
                log_status(agent_id, "[SUCCESS] Cookie Injected")
            except Exception as ce:
                log_status(agent_id, f"[ERROR] Cookie Denied: {str(ce)[:30]}")
                driver.quit()
                continue

            # 4. Refresh & Navigate to Chat
            driver.refresh()
            time.sleep(5)
            driver.get(f"https://www.instagram.com/direct/t/{target}/")
            time.sleep(5)
            
            # --- REMAINING SLIDER LOGIC ---
            log_status(agent_id, "[LISTEN] Monitoring Chat...")
            last_seen = get_last_message_text(driver)

            while (time.time() - session_start) < SESSION_MIN_SEC:
                if (time.time() - global_start) > TOTAL_DURATION: break
                
                msg_box = find_mobile_box(driver)
                current_text = get_last_message_text(driver)

                if current_text and current_text != last_seen:
                    log_status(agent_id, f"[SLIDE] New: {current_text[:20]}")
                    time.sleep(random.uniform(2, 5))
                    reply = random.choice(messages)
                    if adaptive_inject(driver, msg_box, reply):
                        log_status(agent_id, f"[SENT] >> {reply}")
                        last_seen = reply
                
                time.sleep(2)
