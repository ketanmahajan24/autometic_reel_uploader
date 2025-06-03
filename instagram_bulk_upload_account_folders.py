import instagrapi
import csv
import time
import schedule
import datetime
import json
import os
import random

# Configuration
DELAY_BETWEEN_UPLOADS = 30  # Delay in seconds between uploads
RANDOM_CAPTIONS = [
    "Check out this awesome video! 🔥 #Reels",
    "New content alert! 🚀 #Instagram",
    "Enjoy the vibes! 🎥 #DailyPost",
    "Something exciting for you! ✨ #Video",
    "Don't miss this! 😎 #ReelIt"
]
BASE_VIDEO_DIR = "videos"

# Load accounts
def load_accounts():
    try:
        with open('accounts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("accounts.json not found.")
        return []

# Save upload details
def save_post_details(post_id, username, video_path, caption, upload_time):
    with open('post_history.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([post_id, username, video_path, caption, upload_time])

# Login using session_id
def login(account):
    cl = instagrapi.Client()
    try:
        cl.login_by_sessionid(account['session_id'])
        print(f"✅ Logged in with session_id for {account['username']}")
        return cl
    except Exception as e:
        print(f"❌ Login failed for {account['username']}: {e}")
        return None

# Upload a single video
def upload_video(cl, video_path, caption):
    try:
        if not os.path.exists(video_path) and not video_path.startswith('http'):
            print(f"❌ File not found: {video_path}")
            return None, None

        final_caption = caption if caption else random.choice(RANDOM_CAPTIONS)
        media = cl.video_upload(video_path, caption=final_caption)
        print(f"✅ Uploaded: {video_path} | Caption: {final_caption}")
        return media.pk, final_caption
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None, None

# Upload videos for an account
def upload_for_account(account):
    username = account['username']
    print(f"📤 Starting upload for {username} at {datetime.datetime.now()}")

    account_video_dir = os.path.join(BASE_VIDEO_DIR, username)
    if not os.path.exists(account_video_dir):
        os.makedirs(account_video_dir)

    videos = []
    try:
        with open('videos.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) < 4:
                    continue
                vid_username, video_path, caption, order = row[:4]
                if vid_username == username:
                    full_path = os.path.join(account_video_dir, video_path) if not video_path.startswith('http') else video_path
                    videos.append({
                        'video_path': full_path,
                        'caption': caption,
                        'order': int(order) if order else float('inf')
                    })
    except Exception as e:
        print(f"❌ Error reading videos.csv: {e}")
        return

    videos.sort(key=lambda x: x['order'])

    cl = login(account)
    if not cl:
        return

    for video in videos:
        video_path = video['video_path']
        post_id, used_caption = upload_video(cl, video_path, video['caption'])
        if post_id:
            save_post_details(post_id, username, video_path, used_caption, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(DELAY_BETWEEN_UPLOADS)

# Main script
def main():
    if not os.path.exists(BASE_VIDEO_DIR):
        os.makedirs(BASE_VIDEO_DIR)

    with open('post_history.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['post_id', 'username', 'video_path', 'caption', 'upload_time'])

    accounts = load_accounts()
    for account in accounts:
        upload_times = account.get('upload_times', [])
        if not upload_times:
            upload_times = [account.get('upload_time', '10:00')]

        for upload_time in upload_times:
            try:
                datetime.datetime.strptime(upload_time, '%H:%M')
                schedule.every().day.at(upload_time).do(upload_for_account, account=account)
                print(f"🕒 Scheduled {account['username']} at {upload_time}")
            except ValueError:
                print(f"❌ Invalid time: {upload_time} for {account['username']}")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
