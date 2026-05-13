import time
import socket
import logging
from datetime import datetime
from config_manager import load_config
from notifier import send_telegram_alert

def check_connection(hostname, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        result = sock.connect_ex((hostname, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def run_monitor():
    config = load_config()
    log_file = config.get("log_file", "vps_health.log")
    
    # Configure logging
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info("VPS Health Monitor started.")
    
    # State tracking: mapping of (hostname, port) to consecutive failure counts
    failure_counts = {}
    # Track if an alert has already been sent to avoid spamming
    alert_sent = {}
    
    while True:
        # Reload config in case it changed
        config = load_config()
        targets = config.get("targets", [])
        
        if not targets:
            time.sleep(10)
            continue
            
        for target in targets:
            hostname = target["hostname"]
            port = target["port"]
            max_retries = target["max_retries"]
            
            target_key = f"{hostname}:{port}"
            
            is_up = check_connection(hostname, port)
            
            if is_up:
                if failure_counts.get(target_key, 0) > 0:
                    logging.info(f"{target_key} is back ONLINE.")
                    if alert_sent.get(target_key, False):
                        send_telegram_alert(f"✅ Host *{target_key}* is back ONLINE.")
                        alert_sent[target_key] = False
                failure_counts[target_key] = 0
            else:
                failure_counts[target_key] = failure_counts.get(target_key, 0) + 1
                logging.warning(f"Connection to {target_key} failed (Attempt {failure_counts[target_key]}/{max_retries}).")
                
                if failure_counts[target_key] >= max_retries and not alert_sent.get(target_key, False):
                    logging.error(f"{target_key} is DOWN! Sending Telegram alert.")
                    send_telegram_alert(f"🔴 Host *{target_key}* is DOWN!\nFailed {failure_counts[target_key]} consecutive checks.")
                    alert_sent[target_key] = True
                    
        # Find the minimum check interval to sleep, or default to 60s
        if targets:
            sleep_time = min(t["check_interval"] for t in targets)
        else:
            sleep_time = 60
            
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_monitor()
