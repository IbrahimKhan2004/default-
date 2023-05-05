from string import ascii_lowercase, digits
from random import choices
from shutil import rmtree
from config import Config


LOGGER = Config.LOGGER



############Helper Functions##############
def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


###############------Generate_Random_String------###############
def gen_random_string(k):
    return str(''.join(choices(ascii_lowercase + digits, k=k)))



###############------Remove_Directory------###############
def remove_dir(dir):
    try:
        rmtree(dir)
        LOGGER.info(f'successfully deleted directory {dir}')
    except Exception as e:
        LOGGER.info(f'failed to delete directory {dir} : {str(e)}')
    return


###############------Size_Functions------###############
def get_human_size(num, format='B'):
    base = 1024.0
    if format=='B':
            sufix_list = ['B','KB','MB','GB','TB','PB','EB','ZB', 'YB']
    elif format=='KB':
            sufix_list = ['KB','MB','GB','TB','PB','EB','ZB', 'YB']
    elif format=='MB':
            sufix_list = ['MB','GB','TB','PB','EB','ZB', 'YB']
    for unit in sufix_list:
        if abs(num) < base:
            return f"{round(num, 2)} {unit}"
        num /= base