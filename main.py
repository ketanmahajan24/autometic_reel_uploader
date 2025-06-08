import os
import time
import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes, ClientError
import schedule
from concurrent.futures import ThreadPoolExecutor

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_DIR = "A:/REELS_FOLDER"
MAX_RETRIES = 3
MAX_THREADS = 3
executor = ThreadPoolExecutor(max_workers=MAX_THREADS)

# Account Configs
accounts = [
    {
        "username": "bgmi_hacks1",
        "password": "890890",
        "upload_times": ["12:00", "15:00", "18:00", "21:00", "00:00", "03:00", "06:00", "09:00"],
        "upload_delay": 30,
        "caption": "🔥#Hack download link 🖇️ bio #bgmi #pubg #trending #battlegroundmobileindia #bgmifunny #funny #pubgmoments #bgmilovers❤️ #feed #explore #pubgmoments #pubgm #pubgmobile #pubgvideos #pubgmeme #pubgfunny #fyp #pub"
    },
    {
        "username": "bgmi_hack07",
        "password": "890890",
        "upload_times": ["13:30", "16:30", "19:30", "22:30", "01:30", "04:30", "07:30", "10:30"],
        "upload_delay": 30,
        "caption": "💥 #Hack download link 🖇️ bio #bgmi #pubg #trending #battlegroundmobileindia #bgmifunny #funny #pubgmoments #bgmilovers❤️ #feed #explore #pubgmoments #pubgm #pubgmobile #pubgvideos #pubgmeme #pubgfunny #fyp #pub"
    }
]

def load_client(username):
    cl = Client()
    cl.set_device({"manufacturer": "OnePlus", "model": "6T", "android_version": 29})
    session_path = f"session_{username}.json"
    try:
        if os.path.exists(session_path):
            cl.load_settings(session_path)
            cl.login(username, None)
            logging.info(f"✅ Session loaded for {username}")
        else:
            raise FileNotFoundError
    except (LoginRequired, FileNotFoundError):
        logging.warning(f"🔐 Login required for {username}")
        password = next(acc['password'] for acc in accounts if acc['username'] == username)
        cl.login(username, password)
        cl.dump_settings(session_path)
        logging.info(f"💾 New session saved for {username}")
    return cl

def upload_video(cl, video_path, caption):
    for attempt in range(MAX_RETRIES):
        try:
            logging.info(f"⬆️ Uploading {video_path}")
            cl.clip_upload(video_path, caption)
            logging.info(f"✅ Uploaded: {video_path}")
            return True
        except PleaseWaitFewMinutes:
            wait_time = 60 * (attempt + 1)
            logging.warning(f"⏳ Rate limit. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except ClientError as e:
            logging.error(f"⚠️ Client error: {e}")
            return False
        except Exception as e:
            logging.error(f"❌ Failed to upload {video_path}: {e}")
    return False

def upload_all_videos(username):
    account = next(acc for acc in accounts if acc["username"] == username)
    upload_delay = account.get("upload_delay", 10)
    caption = account.get("caption", "")
    cl = load_client(username)

    folder = os.path.join(BASE_DIR, username)
    if not os.path.isdir(folder):
        logging.warning(f"📁 Folder not found for {username}")
        return

    files = sorted([f for f in os.listdir(folder) if f.endswith(".mp4")])
    for file in files:
        path = os.path.join(folder, file)
        success = upload_video(cl, path, caption)
        if not success:
            logging.error(f"⚠️ Skipped: {file}")
        time.sleep(upload_delay)

def schedule_upload(account):
    for t in account["upload_times"]:
        schedule.every().day.at(t).do(lambda acc=account["username"]: executor.submit(upload_all_videos, acc))
        logging.info(f"📅 Scheduled {account['username']} at {t}")

def main():
    for account in accounts:
        schedule_upload(account)
    logging.info("✅ Scheduling ready. Waiting for next task...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
