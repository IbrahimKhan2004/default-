from os.path import isdir
from os import makedirs
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from bot_helper.Rclone.Rclone_Status import RcloneStatus


def create_direc(direc):
    if not isdir(direc):
        makedirs(direc)
    return



async def upload_to_drive(client, staus_message, process_id, process_dir, log_dir, base, rclone_config_loc, drive_name, filename, file_type):
                log_file = f"{log_dir}/Rclone_Upload_Logs.txt"
                create_direc(log_dir)
                command =  [ "rclone",
                                                "copy",
                                                f"--config={rclone_config_loc}",
                                                f'{str(process_dir)}',
                                                f"{drive_name}:{base}/",
                                                "-f",
                                                "- *.!qB",
                                                "--buffer-size=1M",
                                                "-P"]
                process = await create_subprocess_exec(
                                                                                                *command,
                                                                                                stdout=PIPE,
                                                                                                stderr=PIPE,
                                                                                                )
                return RcloneStatus(client, staus_message, process, process_id, log_file, process_dir, command, drive_name, rclone_config_loc, base, filename, file_type)