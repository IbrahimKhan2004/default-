from config import Config
from pyromod import listen
from pyrogram import Client, idle



app = Client(
    "Mega-Bypass_Bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="bot"),
)


if __name__ == "__main__":
    app.start()
    uname = app.get_me().username
    print(f'✅@{uname} Started Successfully!✅')
    print(f"⚡Bot By Sahil Nolia⚡")
    idle()
    app.stop()
    print("💀Bot Stopped💀")
