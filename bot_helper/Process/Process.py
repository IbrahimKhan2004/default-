


class MasterProcess:
    def __init__(self, client, message, chat_id, staus_message, process,process_id, process_dir, log_dir, source_url):
        self.client = client
        self.message = message
        self.chat_id = chat_id
        self.staus_message = staus_message
        self.process = process
        self.process_id = process_id
        self.process_dir = process_dir
        self.log_dir = log_dir
        self.source_url = source_url
        self.msg = False
        
        
    def save_message(self, text):
        self.msg = text
        return
    
    def change_process(self, process):
        self.process = process
        return