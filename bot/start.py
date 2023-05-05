from pyrogram import Client,  filters
from time import time
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_helper.Helper import get_readable_time, gen_random_string, remove_dir
from bot_helper.Mega.Mega_Downloader import mega_downloader
from bot_helper.Process.Runnig_Process import append_running_process, remove_running_process
from asyncio import create_task, gather as asyncio_gather
from bot_helper.Process.Process import MasterProcess
from bot_helper.Status import update_status
from os.path import exists, join as os_join
from bot_helper.Rclone.Rclone_Uploader import upload_to_drive


############Variables##############
LOGGER = Config.LOGGER
DRIVE_BASE_DIR = Config.DRIVE_BASE_DIR
rclone_config_loc = './rclone.conf'
drive_name = "kindle"


################Functions####################
async def verfiy_process(client, message, chat_id, process, process_id, master_process, process_dir, log_dir):
    if not process.cancelled:
            if not process.completed:
                if process.type()=='Mega':
                        error_message = f'❗[Mega]({process.url}) **Download Failed**'
                        file_not_found = f'❗[Mega]({process.url}) **Download Error Log File Not Found**'
                elif process.type()=='Rclone':
                        error_message = f'❗**Failed To Upload** `{process.name()}` To `{process.drive_name}`'
                        file_not_found = f'❗`{process.name()}` **Upload Error Log File Not Found**'
                if exists(process.log_file):
                        await client.send_document(chat_id=chat_id, document=process.log_file, caption=error_message)
                else:
                    await message.reply(file_not_found, quote=True)
                if process.error:
                        LOGGER.info(f'{process.type()} Error Logs Found')
                        error_message = str(process.error)
                master_process.save_message(error_message)
                remove_dir(process_dir)
                remove_dir(log_dir)
                await remove_running_process(process_id)
                return False
            elif process.type()=='Rclone':
                success_msg = f'✅**Successfully Upload To** `{process.drive_name}`\n\n⏺Name: [{process.name()}]({master_process.source_url})'
                if process.link:
                    success_msg = success_msg + f'\n\n🔗Link: `{process.link}`'
                else:
                    success_msg = success_msg + f'\n\n❗Failed To Get Link'
                master_process.save_message(success_msg)
                remove_dir(process_dir)
                remove_dir(log_dir)
                await remove_running_process(process_id)
            return True
    else:
        return False

def is_mega_link(url):
    if "mega.nz" in url or "mega.co.nz" in url:
        return url
    else:
        return False

def get_mega_link_type(url):
    if "folder" in url:
        return "folder"
    elif "file" in url:
        return "file"
    elif "/#F!" in url:
        return "folder"
    return "file"

################Start####################
@Client.on_message(filters.command('start'))
async def start_message(client, message):
    text = f"Hi {message.from_user.mention(style='md')}, I Am A Voter ID Card Download Bot By Sahil."
    await client.send_message(chat_id=message.chat.id,
                                text=text,reply_markup=InlineKeyboardMarkup(
                            [[
                                    InlineKeyboardButton(
                                        f'⭐ Bot By 𝚂𝚊𝚑𝚒𝚕 ⭐',
                                        url='https://t.me/nik66')
                                ], [
                                    InlineKeyboardButton(
                                        f'❤ Join Channel ❤',
                                        url='https://t.me/nik66x')
                                ]]
                        ))
    return


################Time####################
@Client.on_message(filters.command(["time"]))
async def uptime(client, message):
        currentTime = get_readable_time(time() - Config.botStartTime)
        await client.send_message(chat_id=message.chat.id,
                                text=f'♻Bot Is Alive For {currentTime}')
        return


################Cancel Process###########
@Client.on_message(filters.command(["cancel"]))
async def cancel(client, message):
        chat_id = message.chat.id
        if len(message.command)==2:
                process_id = message.command[1]
                cancelled = await remove_running_process(process_id)
                if cancelled:
                    await cancelled.reply("✅Successfully Cancelled.", quote=True)
                else:
                    await client.send_message(chat_id=chat_id,
                                text=f'❗No Running Processs With This ID')
        else:
                await client.send_message(chat_id=chat_id,
                                        text=f'❗Give Me Process ID To Cancel.')





######################Mega######################
@Client.on_message(filters.private & filters.command(["mirrormega"]))
async def mirror_mega(client, message):
    chat_id = message.chat.id
    if len(message.command)==2:
        mega_link = is_mega_link(message.command[1])
    else:
            try:
                    ask = await client.ask(chat_id, '*️⃣ Send Mega Link\n\n⏳Time Out: 120 Seconds', timeout=120, filters=filters.text)
                    mega_link = ask.text
            except:
                    await client.send_message(chat_id, "🔃Timed Out! Tasked Has Been Cancelled.")
                    return
            await ask.request.delete()
    LOGGER.info(f"Mega Link Found: {mega_link}")
    staus_message = await client.send_message(chat_id=chat_id,
                                text=f"🔶Please Wait....", reply_to_message_id=message.id)
    process_id = gen_random_string(7)
    process_dir = os_join(Config.DOWNLOAD_PATH, process_id)
    log_dir = os_join(Config.LOGS_PATH, process_id)
    await append_running_process(process_id, message)
    mega_status = await mega_downloader(client, staus_message, mega_link, process_id, process_dir, log_dir)
    master_process = MasterProcess(client, message, chat_id, staus_message, mega_status, process_id, process_dir, log_dir, mega_link)
    updater_task = create_task(update_status(master_process))
    await mega_status.status_updater()
    if (await verfiy_process(client, message, chat_id, mega_status, process_id, master_process, process_dir, log_dir)):
        LOGGER.info(f'🔼Uploading {mega_status.name()} To {drive_name}')
        rclone_process = await upload_to_drive(client, staus_message, process_id, process_dir, log_dir, DRIVE_BASE_DIR, rclone_config_loc, drive_name, mega_status.name(), mega_status.file_type)
        master_process.change_process(rclone_process)
        await rclone_process.status_updater()
        await verfiy_process(client, message, chat_id, rclone_process, process_id, master_process, process_dir, log_dir)
        
    LOGGER.info((await asyncio_gather(updater_task, return_exceptions=True)))

