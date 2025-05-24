import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
OWNER_ID = int(os.getenv("OWNER_ID", "2119921139"))
ADMIN_ACCESS = {OWNER_ID: []}

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_ACCESS

def has_access(user_id: int, username: str) -> bool:
    if is_owner(user_id):
        return True
    return username in ADMIN_ACCESS.get(user_id, [])

async def check_access(update: Update, username: str) -> bool:
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Unauthorized user.")
        return False
    if not has_access(user_id, username):
        await update.message.reply_text("❌ No access to this account.")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data='status')],
        [InlineKeyboardButton("⏸ Pause", callback_data='pause'),
         InlineKeyboardButton("▶ Resume", callback_data='resume')],
        [InlineKeyboardButton("⏰ Set Schedule", callback_data='set_schedule')],
        [InlineKeyboardButton("⚡ Force Upload", callback_data='force_upload')],
        [InlineKeyboardButton("➕ Add Account", callback_data='add_account'),
         InlineKeyboardButton("➖ Remove Account", callback_data='remove_account')],
        [InlineKeyboardButton("📝 Logs", callback_data='logs')],
        [InlineKeyboardButton("👤 Owner", callback_data='owner')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    await update.message.reply_text('✅ Bot Control Panel', reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = {
        'status': "Send command: /status <username>",
        'pause': "Send command: /pause <username>",
        'resume': "Send command: /resume <username>",
        'set_schedule': "Send command: /set_schedule <username> <time1,time2,...>",
        'force_upload': "Send command: /force_upload <username> <video_path> [caption]",
        'add_account': "Send command: /add_account <username> <password>",
        'remove_account': "Send command: /remove_account <username>",
        'logs': "Send command: /logs <username>",
        'owner': "CONTACT OWNER FOR ANY ISSUE :- @LUCIFERCHEAT",
        'help': (
            "Bot Commands:\n"
            "/start - Show control panel\n"
            "/status <username>\n"
            "/pause <username>\n"
            "/resume <username>\n"
            "/set_schedule <username> <time1,time2,...>\n"
            "/force_upload <username> <video_path> [caption]\n"
            "/add_account <username> <password>\n"
            "/remove_account <username>\n"
            "/add_admin <user_id> <usernames>\n"
            "/remove_admin <user_id>\n"
            "/admins"
        )
    }
    await query.edit_message_text(msg.get(query.data, "Unknown command."))

# Command handlers

async def status(update, context):
    await generic_handler(update, context, "status")

async def pause(update, context):
    await generic_handler(update, context, "pause")

async def resume(update, context):
    await generic_handler(update, context, "resume")

async def logs(update, context):
    await generic_handler(update, context, "logs")

async def force_upload(update, context):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /force_upload <username> <video_path> [caption]")
        return
    username = context.args[0]
    video_path = context.args[1]
    caption = " ".join(context.args[2:]) if len(context.args) > 2 else ""
    if not await check_access(update, username): return
    uploader = context.bot_data['uploader']
    uploader.force_upload(username, video_path, caption)
    await update.message.reply_text(f"⚡ Forced upload for {username} with video {video_path}.")

async def set_schedule(update, context):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /set_schedule <username> <time1,time2,...>")
        return
    username = context.args[0]
    times_str = context.args[1]
    if not await check_access(update, username): return
    times = times_str.split(',')
    context.bot_data['uploader'].set_schedule(username, times)
    await update.message.reply_text(f"⏰ Schedule updated for {username}: {times}")

async def add_account(update, context):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Owner only.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_account <username> <password>")
        return
    username = context.args[0]
    password = context.args[1]
    success = context.bot_data['uploader'].add_account(username, password)
    if success:
        await update.message.reply_text(f"✅ Added {username}.")
    else:
        await update.message.reply_text(f"❌ Failed to add {username}.")

async def remove_account(update, context):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Owner only.")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /remove_account <username>")
        return
    username = context.args[0]
    success = context.bot_data['uploader'].remove_account(username)
    if success:
        await update.message.reply_text(f"✅ Removed {username}.")
    else:
        await update.message.reply_text(f"❌ Account {username} not found.")

async def list_admins(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only.")
    msg = "Admins:\n"
    for aid, users in ADMIN_ACCESS.items():
        msg += f"{'Owner' if aid == OWNER_ID else 'Admin'} {aid} -> {users}\n"
    await update.message.reply_text(msg)

async def generic_handler(update, context, action):
    if not context.args:
        await update.message.reply_text(f"Usage: /{action} <username>")
        return
    username = context.args[0]
    if not await check_access(update, username): return
    uploader = context.bot_data['uploader']
    if action == "status" or action == "logs":
        logs = uploader.get_logs(username)
        await update.message.reply_text(f"{action.title()} for {username}:\n" + "\n".join(logs))
    elif action == "pause":
        uploader.pause(username)
        await update.message.reply_text(f"⏸ Paused {username}.")
    elif action == "resume":
        uploader.resume(username)
        await update.message.reply_text(f"▶ Resumed {username}.")

def start_telegram_bot(uploader):
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.bot_data['uploader'] = uploader

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("pause", pause))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("set_schedule", set_schedule))
    app.add_handler(CommandHandler("force_upload", force_upload))
    app.add_handler(CommandHandler("add_account", add_account))
    app.add_handler(CommandHandler("remove_account", remove_account))
    app.add_handler(CommandHandler("admins", list_admins))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Telegram bot started...")
    app.run_polling()
