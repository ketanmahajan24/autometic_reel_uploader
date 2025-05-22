import os
import time
import json
import threading
from instagrapi import Client

# Load account configurations
with open("config.json", "r") as f:
    ACCOUNTS = json.load(f)

# Common caption
BASE_CAPTION = (
    "HACK LINK IN BIO! #bgmi #trendingreels #bgmilovers #viral #trendingaudio "
    "#bgmihack #pubg #trendingsongs #pubgmobile #explore #battlegroundmobileindia "
    "#bgmifunny #funny #pubgmoments #pubgmeme #pubgfunny #fyp"
)

def upload_loop(account):
    username = account["username"]
    password = account["password"]
    folder = account["reels_folder"]
    upload_interval = account["upload_interval"]
    loop_interval = account["loop_interval"]

    # Auto-create folders
    os.makedirs(folder, exist_ok=True)

    # Login to Instagram
    cl = Client()
    try:
        cl.login(username, password)
        print(f"[{username}] ✅ Logged in.")
    except Exception as e:
        print(f"[{username}] ❌ Login failed: {e}")
        return

    while True:
        new_upload = False

        # DO NOT TRACK uploaded files
        for filename in os.listdir(folder):
            if filename.endswith(".mp4"):
                filepath = os.path.join(folder, filename)
                try:
                    print(f"[{username}] 📤 Uploading {filename}...")
                    cl.clip_upload(filepath, caption=f"{BASE_CAPTION} — {filename}")
                    print(f"[{username}] ✅ Uploaded {filename}")

                    new_upload = True
                    time.sleep(upload_interval)

                except Exception as e:
                    print(f"[{username}] ❌ Failed to upload {filename}: {e}")

        if not new_upload:
            print(f"[{username}] ⏳ No new reels. Waiting {loop_interval // 60} minutes...")
        time.sleep(loop_interval)

# Start each account in a separate thread
for account in ACCOUNTS:
    thread = threading.Thread(target=upload_loop, args=(account,), daemon=True)
    thread.start()

# Keep the main thread alive
while True:
    time.sleep(60)
