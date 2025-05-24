from instagrapi import Client

class UploadManager:
    def __init__(self, accounts, passwords):
        self.clients = {}
        self.status = {}
        self.logs_data = {}
        self.schedules = {}
        self.paused = {}

        for username, password in zip(accounts, passwords):
            cl = Client()
            try:
                cl.login(username, password)
                self.clients[username] = cl
                self.status[username] = "Active"
                self.logs_data[username] = ["✅ Logged in"]
            except Exception as e:
                self.logs_data[username] = [f"❌ Failed to log in: {str(e)}"]

    def get_logs(self, username):
        return self.logs_data.get(username, ["No logs available."])

    def pause(self, username):
        self.paused[username] = True
        self.logs_data.setdefault(username, []).append("⏸️ Paused uploads")

    def resume(self, username):
        self.paused[username] = False
        self.logs_data.setdefault(username, []).append("▶️ Resumed uploads")

    def add_account(self, username, password):
        cl = Client()
        try:
            cl.login(username, password)
            self.clients[username] = cl
            self.status[username] = "Active"
            self.logs_data[username] = ["✅ Account added"]
            return True
        except Exception as e:
            self.logs_data[username] = [f"❌ Failed to add: {str(e)}"]
            return False

    def remove_account(self, username):
        if username in self.clients:
            del self.clients[username]
            self.status.pop(username, None)
            self.logs_data.pop(username, None)
            return True
        return False

    def force_upload(self, username, video_path, caption=""):
        if username not in self.clients:
            self.logs_data.setdefault(username, []).append("❌ Not logged in")
            return

        cl = self.clients[username]
        try:
            cl.clip_upload(video_path, caption)
            self.logs_data[username].append(f"✅ Uploaded {video_path}")
        except Exception as e:
            self.logs_data[username].append(f"❌ Upload failed: {str(e)}")

    def set_schedule(self, username, times):
        self.schedules[username] = times
        self.logs_data.setdefault(username, []).append(f"🕒 Schedule set to: {times}")
