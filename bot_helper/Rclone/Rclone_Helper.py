from configparser import ConfigParser
from json import loads as jsonloads
from re import escape as rescape
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from config import Config


LOGGER = Config.LOGGER



def check_isGdrive(remote, config_file):
        conf = ConfigParser()
        conf.read(config_file)
        for r in conf.sections():
            if str(r) == remote:
                if conf[r]['type'] == 'drive':
                    return True
                else:
                    return False


async def get_drive_link(remote, base, name, conf, file_type):
    if file_type == "Folder":
        s_name = rescape(name.replace(".", ""))
        cmd = ["rclone", "lsjson", f'--config={conf}', f"{remote}:{base}", "--dirs-only", "-f", f"+ {s_name}/", "-f", "- *"]
    else:
        s_name = rescape(name)
        cmd = ["rclone", "lsjson", f'--config={conf}', f"{remote}:{base}", "--files-only", "-f", f"+ {s_name}", "-f", "- *"]
    process = await create_subprocess_exec(*cmd,stdout= PIPE,stderr= PIPE)
    stdout, stderr = await process.communicate()
    return_code = await process.wait()
    stdout = stdout.decode().strip()
    if return_code != 0:
        err = stderr.decode().strip()
        LOGGER.error(f'Error while getting gdrive link: {err}') 
        return False
    try:
        data = jsonloads(stdout)
        id = data[0]["ID"]
        if file_type == "Folder":
            link = f'https://drive.google.com/drive/folders/{id}'
        else:
            link = f'https://drive.google.com/uc?id={id}&export=download'
        return link
    except Exception:
        LOGGER.error("Error while getting gdrive id")
        return False



async def rclone_get_link(remote, base, name, conf, file_type):
        cmd =  ["rclone", "link", f'--config={conf}', f"{remote}:{base}/{name}"]
        LOGGER.info(f"Getting Uploaded File {name} Link From {remote}")
        process = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
        out, _ = await process.communicate()
        url = out.decode().strip()
        return_code = await process.wait()
        if return_code == 0:
                return url
        else:
            if check_isGdrive(remote, conf):
                return await get_drive_link(remote, base, name, conf, file_type)
            else:
                return False