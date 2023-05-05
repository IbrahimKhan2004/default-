from os.path import isdir
from os import makedirs
from subprocess import Popen, PIPE, STDOUT
from bot_helper.Mega.Mega_Status import MegaStatus
from config import Config


LOGGER = Config.LOGGER


def create_direc(direc):
    if not isdir(direc):
        makedirs(direc)
    return


async def mega_downloader(client, staus_message, url, process_id, process_dir, log_dir):
                    log_file = f"{log_dir}/Mega_Download_Logs.txt"
                    create_direc(process_dir)
                    create_direc(log_dir)
                    command =  ["mega-get", "--ignore-quota-warn", url, process_dir]
                    LOGGER.info(str(command))
                    process = Popen(
                        command,
                        stdout=PIPE,
                        stderr=STDOUT,
                        universal_newlines=True,
                    )
                    return MegaStatus(client, staus_message, process, process_id, log_file, process_dir, command, url)