from instagrapi import Client

def get_sessionid(username, password):
    cl = Client()
    try:
        cl.login(username, password)
        sessionid = cl.get_settings()['authorization_data']['sessionid']
        print(f"✅ Logged in as {username}")
        print(f"Session ID: {sessionid}")
        with open(f"{username}_sessionid.txt", "w") as f:
            f.write(sessionid)
        print(f"✅ Session ID saved to {username}_sessionid.txt")
    except Exception as e:
        print(f"❌ Login failed for {username}: {e}")

if __name__ == "__main__":
    import getpass
    username = input("Enter Instagram username: ")
    password = getpass.getpass("Enter Instagram password: ")
    get_sessionid(username, password)
