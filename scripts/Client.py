import json
from FileSynchronization import FileSynchronization

FS = FileSynchronization('192.168.100.15')
FS.get_files_path('../../BillCalculator/data')
FS.check_modified_time()

# get server files infomation
FS.get_server_files_info()

# process files information
FS.process_files_info()

FS.generate_client_request()
