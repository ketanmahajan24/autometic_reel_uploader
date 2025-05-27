from instagrapi import Client
import os
import time

# Instagram credentials from environment variables (safer than hardcoding)
USERNAME = os.getenv("bgmi_hack07")
PASSWORD = os.getenv("890890")

if not USERNAME or not PASSWORD:
    raise Exception("Instagram credentials not found in environment variables.")

# Login to Instagram
cl = Client()
cl.login(USERNAME, PASSWORD)

# Folder containing reels
REELS_FOLDER = "./reels"

# Track uploaded files to prevent re-uploading
UPLOADED_TRACK_FILE = "uploaded.txt"
if os.path.exists(UPLOADED_TRACK_FILE):
    with open(UPLOADED_TRACK_FILE, "r") as f:
        uploaded_files = set(f.read().splitlines())
else:
    uploaded_files = set()

# Base caption for all uploads
BASE_CAPTION = (
    "HACK LINK IN BIO! #bgmi #trendingreels #bgmilovers #viral #trendingaudio "
    "#bgmihack #pubg #trendingsongs #pubgmobile #explore #battlegroundmobileindia "
    "#bgmifunny #funny #pubgmoments #pubgmeme #pubgfunny #fyp"
)

# Infinite upload loop
while True:
    new_upload = False

    for filename in os.listdir(REELS_FOLDER):
        if filename.endswith(".mp4") and filename not in uploaded_files:
            filepath = os.path.join(REELS_FOLDER, filename)

            try:
                print(f"📤 Uploading {filename}...")
                cl.clip_upload(
                    filepath,
                    caption=f"{BASE_CAPTION} — {filename}"
                )
                print(f"✅ Uploaded {filename} successfully.")

                # Save to uploaded tracker
                uploaded_files.add(filename)
                with open(UPLOADED_TRACK_FILE, "a") as f:
                    f.write(f"{filename}\n")

                new_upload = True
                time.sleep(180)  # Wait between uploads to mimic human behavior

            except Exception as e:
                print(f"❌ Failed to upload {filename}: {e}")

    if not new_upload:
        print("⏳ No new reels to upload. Waiting 5 minutes...")
    time.sleep(600)  # Check again after 5 minutes

