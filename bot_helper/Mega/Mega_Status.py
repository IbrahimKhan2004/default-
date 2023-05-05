from aiofiles import open as aio_open
from contextlib import closing as contextlib_closing
from bot_helper.Process.Runnig_Process import check_running_process
from re import findall
from os import listdir
from os.path import isdir
from config import Config
from bot_helper.Helper import remove_dir
from time import time


LOGGER = Config.LOGGER
newlines = ['\n', '\r\n', '\r']


def mega_status(proc, stream='stdout'):
    stream = getattr(proc, stream)
    with contextlib_closing(stream):
        while True:
            out = []
            last = stream.read(1)
            # Don't loop forever
            if last == '' and proc.poll() is not None:
                break
            while last not in newlines:
                if last == '' and proc.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = ''.join(out)
            yield out


def mega_progress(line):
    downloaded, total, percentage = 0, 0, 0
    dw_data = findall('\((.*)MB:', line)
    per_data = findall('MB:(.*)%', line)
    if len(dw_data):
        datam = str(dw_data[0].strip()).split('/')
        downloaded = datam[0].strip()
        total = datam[1].strip()
    if len(per_data):
        percentage = per_data[0].strip()
    return downloaded, total, percentage


def get_name(process_dir, check_dir=True):
                filename = False
                file_type = 'File'
                names = listdir(process_dir)
                for name in names:
                    if not str(name).endswith('.mega'):
                            if check_dir and isdir(name):
                                    filename = name
                                    file_type = 'Folder'
                                    LOGGER.info(f'Mega Folder Name Found: {name}')
                            else:
                                    if isdir(name):
                                            file_type = 'Folder'
                                    filename = name
                                    LOGGER.info(f'Mega {file_type} Name Found: {name}')
                return filename, file_type



class MegaStatus:
    def __init__(self, client, staus_message, process,process_id, log_file, process_dir, command, url):
        self.client = client
        self.staus_message = staus_message
        self.process = process
        self.process_id = process_id
        self.log_file = log_file
        self.process_dir = process_dir
        self.command = command
        self.url = url
        self.time = time()
        self.downloaded = 0
        self.percentage = 0
        self._size = False
        self._name = False
        self.name_check = 0
        self.returncode = False
        self.cancelled = False
        self.completed = False
        self.error = False
        self.file_type = False
        self.dw_loc = False
        
    
    def size(self):
        return self._size
    
    def name(self):
        return self._name
    
    def type(self):
        return 'Mega'
    
    async def status_updater(self):
        LOGGER.info(f'Initiating Mega Status Updater: {self.process_id}')
        async with aio_open(self.log_file, "a+", encoding="utf-8") as f:
                    await f.write(f'{str(self.command)}\n')
        for line in mega_status(self.process):
            if not check_running_process(self.process_id):
                    break
            print(line)
            self.downloaded, total, self.percentage = mega_progress(line)
            if not self._size:
                self._size = total
            if not self._name and self.name_check<10:
                self.name_check = self.name_check + 1
                name_check, _ = get_name(self.process_dir)
                if name_check:
                            self._name = name_check
                            async with aio_open(self.log_file, "a+", encoding="utf-8") as f:
                                    await f.write(f'FileName: {str(self._name)}\n')
            async with aio_open(self.log_file, "a+", encoding="utf-8") as f:
                    await f.write(f'{str(line)}\n')
        LOGGER.info(f'Mega Status Updater Completed : {self.process_id}')
        if check_running_process(self.process_id):
            self.process.wait()
            self.returncode = self.process.returncode
            LOGGER.info(f'Mega Status Updater Return Code : {self.returncode}')
            if self.returncode==0:
                self.completed = True
                final_name_check, file_type = get_name(self.process_dir, check_dir=False)
                if final_name_check:
                            self._name = final_name_check
                            self.file_type = file_type
                else:
                    LOGGER.info(f'Mega File Name Not Found : {self.process_id}')
                    self._name = "Name Not Found"
                LOGGER.info(f'✅Successfully Downloaded {self._name if self._name else self.url} From Mega: {self.process_id}')
            else:
                LOGGER.info(f'❌Failed To Download {self._name if self._name else self.url} From Mega: {self.process_id}')
                async with aio_open(self.log_file, "r", encoding="utf-8") as f:
                            error = await f.read()
                if len(error)<3800:
                    self.error = error
                else:
                    LOGGER.info(f"Mega Error Message Length Greater Than 3800")
        else:
            self.process.kill()
            self.cancelled = True
            remove_dir(self.process_dir)
            LOGGER.info(f'{self.process_id} Process Cancelled : {self._name if self._name else "Unkown Name"}')
        return