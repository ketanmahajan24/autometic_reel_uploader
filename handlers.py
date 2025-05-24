# handlers.py

async def generic_handler(update, context, action, uploader):
    if len(context.args) < 2:
        await update.message.reply_text(f"Usage: /{action} <username> <video_path>")
        return

    username = context.args[0]
    video_path = context.args[1]

    if action == "force_upload":
        uploader.force_upload(username, video_path)
        await update.message.reply_text(f"✅ Upload triggered for {username} with video {video_path}")
    else:
        await update.message.reply_text(f"❌ Unknown action: {action}")
