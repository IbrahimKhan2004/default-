from bot_helper.Process.Runnig_Process import check_running_process
from bot_helper.Helper import get_human_size, get_readable_time
from config import Config
from pyrogram.errors import exceptions as Pyrogram_Exception
from pyrogram.errors import FloodWait
from asyncio import sleep as asyncio_sleep
from time import time


LOGGER = Config.LOGGER
STATUS_UPDATE_TIME = Config.STATUS_UPDATE_TIME


def get_progress_bar_from_percentage(percentage):
    try:
        p = str(percentage).strip().strip("%")
        p = int(p)
    except Exception as e:
        LOGGER.info(f'error in getting progress bar from percentage: {str(e)}')
        p = 0
    p = min(max(p, 0), 100)
    cFull = p // 8
    p_str = Config.FINISHED_PROGRESS_STR * cFull
    p_str += Config.UNFINISHED_PROGRESS_STR * (12 - cFull)
    return f"[{p_str}]"


def get_progress_bar_string(current,total):
    try:
        current = int(current)
        total = int(total)
        completed = int(current) / 8
        total = int(total) / 8
        p = 0 if total == 0 else round(completed * 100 / total)
    except Exception as e:
        LOGGER.info(f'error in getting progress bar from string: {str(e)}')
        p = 0
    p = min(max(p, 0), 100)
    cFull = p // 8
    p_str = Config.FINISHED_PROGRESS_STR * cFull
    p_str += Config.UNFINISHED_PROGRESS_STR * (12 - cFull)
    return f"[{p_str}]"


def get_speed(current, start_time):
    try:
            return float(current) / round(time() - start_time)
    except Exception as e:
            LOGGER.info(f'error in getting speed: {str(e)}')
            return False


def get_eta(current, total, speed):
    try:
        return(float(total)-float(current))/speed
    except Exception as e:
        LOGGER.info(f'error in getting eta: {str(e)}')
        return "-/-"

def get_speed_eta(proc):
        speed = get_speed(proc.downloaded, proc.time)
        if speed:
            eta = get_eta(proc.downloaded, proc.size(), speed)
            return f'**Speed**: {get_human_size(speed, format="MB")}/s | **ETA**: {get_readable_time(eta)}'
        else:
            return f'**Speed**: 0 MB/s | **ETA**: -/-'
        


def get_mega_name(proc):
    if proc.name():
        return "**Name**: " + proc.name() + "\n"
    else:
        return ""



def progress_status(proc):
    if proc.type()== 'Mega':
        status = f'{get_mega_name(proc)}'\
                        f'{get_progress_bar_string(proc.downloaded, proc.size())} {proc.percentage}%\n'\
                        f"**Downloaded**: {proc.downloaded} of {str(proc.size()) if proc.size() else '0'} MB\n"\
                        f'{get_speed_eta(proc)}\n'\
                        f"`/cancel {proc.process_id}`"
    if proc.type()== 'Rclone':
        status = f"**Name**: {proc.name()}\n"\
                        f'{get_progress_bar_from_percentage(proc.percentage)} {proc.percentage}%\n'\
                        f"**Uploaded**: {proc.uploaded} of {str(proc.size()) if proc.size() else '0 MB'}\n"\
                        f'**Speed**: {proc.speed} | **ETA**: {proc.eta}\n'\
                        f"`/cancel {proc.process_id}`"
                        
    return status + f"\n\n**UPTIME:** {get_readable_time(time() - Config.botStartTime)}"



async def update_status(master_process):
    while True:
        if not check_running_process(master_process.process_id):
                await master_process.staus_message.delete()
                if master_process.msg:
                    await master_process.message.reply(master_process.msg, quote=True, disable_web_page_preview=True)
                else:
                    await master_process.message.reply('🔒Task Cancelled By User!', quote=True)
                break
        try:
                await master_process.staus_message.edit(progress_status(master_process.process))
        except Pyrogram_Exception.bad_request_400.MessageNotModified:
                pass
        except FloodWait as e:
                await asyncio_sleep(e.value+10)
        except Exception as e:
                LOGGER.info(f"Error Occured In Updating Status Message: {master_process.process_id}")
                LOGGER.info("Error Type: ", type(e))
        await asyncio_sleep(STATUS_UPDATE_TIME)
    return