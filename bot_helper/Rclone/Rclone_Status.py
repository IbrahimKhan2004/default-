from aiofiles import open as aio_open
from bot_helper.Process.Runnig_Process import check_running_process
from re import findall
from config import Config
from bot_helper.Helper import remove_dir
from bot_helper.Rclone.Rclone_Helper import rclone_get_link


LOGGER = Config.LOGGER




class RcloneStatus:
    def __init__(self, client, staus_message, process, process_id, log_file, process_dir, command, drive_name, rclone_config_loc, base, filename, file_type):
        self.client = client
        self.staus_message = staus_message
        self.process = process
        self.process_id = process_id
        self.log_file = log_file
        self.process_dir = process_dir
        self.command = command
        self.rclone_config_loc = rclone_config_loc
        self.base = base
        self.drive_name = drive_name
        self.uploaded = 0
        self.percentage = 0
        self.speed = '0 MB/s'
        self.eta = '-/-'
        self._size = False
        self._name = filename
        self.file_type = file_type
        self.returncode = False
        self.cancelled = False
        self.completed = False
        self.error = False
        self.link = False
        
    
    def size(self):
        return self._size
    
    def name(self):
        return self._name
    
    def type(self):
        return 'Rclone'
    
    async def status_updater(self):
        LOGGER.info(f'Initiating Rclone Status Updater: {self.process_id}')
        async with aio_open(self.log_file, "a+", encoding="utf-8") as f:
                    await f.write(f'{str(self.command)}\n')
        while True:
            try:
                    async for line in self.process.stdout:
                        if not check_running_process(self.process_id):
                                break
                        line = line.decode().strip()
                        print(line)
                        try:
                            datam = findall("Transferred:.*ETA.*", line)
                            if datam is not None:
                                if len(datam) > 0:
                                        progress = datam[0].replace("Transferred:", "").strip().split(",")
                                        dwdata = progress[0].strip().split('/')
                                        self.uploaded, self._size, self.percentage, self.speed, self.eta = dwdata[0].strip(), dwdata[1].strip(), progress[1].strip("% "), progress[2], progress[3].strip().replace('ETA', '').strip()
                        except Exception as e:
                                LOGGER.info(f'❌Error Getting Rclone Progress: {str(e)}')
                        async with aio_open(self.log_file, "a+", encoding="utf-8") as f:
                                await f.write(f'{str(line)}\n')
            except ValueError:
                    continue
            else:
                    break
        LOGGER.info(f'Rclone Status Updater Completed : {self.process_id}')
        if check_running_process(self.process_id):
            await self.process.wait()
            self.returncode = self.process.returncode
            LOGGER.info(f'Rclone Status Updater Return Code : {self.returncode}')
            if self.returncode==0:
                self.completed = True
                self.link = await rclone_get_link(self.drive_name, self.base, self._name, self.rclone_config_loc, self.file_type)
                LOGGER.info(f'✅Successfully Uploaded {self._name} To {self.drive_name}: {self.process_id}')
            else:
                LOGGER.info(f'❌Failed To Upload {self._name} To {self.drive_name}: {self.process_id}')
                async with aio_open(self.log_file, "r", encoding="utf-8") as f:
                            error = await f.read()
                if len(error)<3800:
                    self.error = error
                else:
                    LOGGER.info(f"Rclone Error Message Length Greater Than 3800")
        else:
            self.process.kill()
            self.cancelled = True
            remove_dir(self.process_dir)
            LOGGER.info(f'{self.process_id} Process Cancelled : {self._name}')
        return


