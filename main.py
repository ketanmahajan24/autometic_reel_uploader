import os
import json
import time
import threading
import datetime
from instagrapi import Client
from telegram.ext import Updater, CommandHandler

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

accounts = config['accounts']
TELEGRAM_BOT_TOKEN = config['telegram']['bot_token']
TELEGRAM_CHAT_ID = str(config['telegram']['chat_id'])

# Initialize Telegram bot
updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher

# Hold clients, uploaded files, and schedule times
clients = {}
uploaded_files = {}
schedule_times = {}

# Setup per account
for acc in accounts:
    username = acc['username']
    password = acc['password']
    reels_folder = acc['reels_folder']
    uploaded_track_file = acc['uploaded_track_file']

    # Create reels folder if missing
    os.makedirs(reels_folder, exist_ok=True)

    # Login to Instagram
    cl = Client()
    cl.login(username, password)
    clients[username] = cl

    # Load uploaded tracker file
    if os.path.exists(uploaded_track_file):
        with open(uploaded_track_file, 'r') as f:
            uploaded_files[username] = set(f.read().splitlines())
    else:
        uploaded_files[username] = set()

    # Load schedule times
    schedule_times[username] = acc.get('schedule_times', [])

# === Upload reels for given account ===
def upload_reels(username, acc):
    cl = clients[username]
    folder = acc['reels_folder']
    caption = acc['caption']
    track_file = acc['uploaded_track_file']

    all_files = [f for f in os.listdir(folder) if f.endswith('.mp4')]
    for file in all_files:
        if file not in uploaded_files[username]:
            try:
                path = os.path.join(folder, file)
                print(f"[{username}] 📤 Uploading {file}")
                cl.clip_upload(path, caption=caption)
                uploaded_files[username].add(file)
                with open(track_file, 'a') as f:
                    f.write(f"{file}\n")
                send_telegram(f"✅ [{username}] Uploaded {file}")
                time.sleep(10)  # slight pause between uploads
            except Exception as e:
                print(f"[{username}] ❌ Failed to upload {file}: {e}")
                send_telegram(f"❌ [{username}] Failed to upload {file}: {e}")

    # Reset tracker if all reels uploaded
    if uploaded_files[username] == set(all_files):
        print(f"[{username}] 🔄 All reels uploaded, resetting tracker")
        uploaded_files[username] = set()
        open(track_file, 'w').close()

# === Scheduler thread ===
def scheduler():
    while True:
        now = datetime.datetime.now().strftime('%H:%M')
        for acc in accounts:
            username = acc['username']
            if now in schedule_times[username]:
                upload_reels(username, acc)
        time.sleep(60)  # check every minute

# === Telegram helpers ===
def send_telegram(msg):
    updater.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

# === Telegram command handlers ===
def list_schedules(update, context):
    msg = "📅 Current Schedules:\n"
    for acc in accounts:
        username = acc['username']
        times = ', '.join(schedule_times[username])
        msg += f"- {username}: {times}\n"
    update.message.reply_text(msg)

def add_time(update, context):
    if len(context.args) < 2:
        update.message.reply_text("Usage: /addtime <username> <HH:MM>")
        return
    username, time_str = context.args[0], context.args[1]
    if username in schedule_times:
        schedule_times[username].append(time_str)
        update.message.reply_text(f"✅ Added {time_str} to {username}")
    else:
        update.message.reply_text(f"❌ Account {username} not found")

def remove_time(update, context):
    if len(context.args) < 2:
        update.message.reply_text("Usage: /removetime <username> <HH:MM>")
        return
    username, time_str = context.args[0], context.args[1]
    if username in schedule_times and time_str in schedule_times[username]:
        schedule_times[username].remove(time_str)
        update.message.reply_text(f"✅ Removed {time_str} from {username}")
    else:
        update.message.reply_text(f"❌ Time or account not found")

def list_videos(update, context):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /listvideos <username>")
        return
    username = context.args[0]
    acc = next((a for a in accounts if a['username'] == username), None)
    if acc:
        files = os.listdir(acc['reels_folder'])
        videos = [f for f in files if f.endswith('.mp4')]
        update.message.reply_text(f"🎬 Videos in {username}:\n" + '\n'.join(videos))
    else:
        update.message.reply_text(f"❌ Account {username} not found")

def reload_videos(update, context):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /reloadvideos <username>")
        return
    username = context.args[0]
    acc = next((a for a in accounts if a['username'] == username), None)
    if acc:
        uploaded_files[username] = set()
        open(acc['uploaded_track_file'], 'w').close()
        update.message.reply_text(f"✅ Tracker for {username} reset")
    else:
        update.message.reply_text(f"❌ Account {username} not found")

# Register Telegram handlers
dp.add_handler(CommandHandler('list', list_schedules))
dp.add_handler(CommandHandler('addtime', add_time))
dp.add_handler(CommandHandler('removetime', remove_time))
dp.add_handler(CommandHandler('listvideos', list_videos))
dp.add_handler(CommandHandler('reloadvideos', reload_videos))

# Start scheduler thread (daemon so it ends on program exit)
threading.Thread(target=scheduler, daemon=True).start()

# Start Telegram bot polling
updater.start_polling()
print("✅ Bot and scheduler running...")
updater.idle()
