import os
from dotenv import load_dotenv
from uploader import UploadManager
from telegram_bot import start_telegram_bot

def main():
    load_dotenv()
    accounts = os.getenv("IG_ACCOUNTS")
    passwords = os.getenv("IG_PASSWORDS")

    if not accounts or not passwords:
        raise RuntimeError("IG_ACCOUNTS or IG_PASSWORDS environment variables missing!")

    accounts = accounts.split(",")
    passwords = passwords.split(",")

    if len(accounts) != len(passwords):
        raise RuntimeError("Number of IG_ACCOUNTS and IG_PASSWORDS must match!")

    uploader = UploadManager(accounts, passwords)

    start_telegram_bot(uploader)

if __name__ == '__main__':
    main()
