"""
此处用来测试命令行的参数是否正确
"""


Cb = "Complete"
Db = "Different"
Ib = "Increment"

def complete_backup(source_folder, target_folder, filter_include=None, filter_exclude=None, show_progress=True):
    print("complete_backup")
    print(source_folder)
    print(target_folder)
    print(filter_include)
    print(filter_exclude)
def diff_backup(source_folder, target_folder, mode=Db):
    print("diff_backup")
    print(source_folder)
    print(target_folder)
def incremental_backup(source_folder, target_folder):
    print("incremental_backup")
    print(source_folder)
    print(target_folder)
def restore_backup(target_folder, restore_folder):
    print("restore_backup")
    print(target_folder)
    print(restore_folder)
def update_to_ftp(ip_address, username, password, local_dir, remote_dir):
    print("update_to_ftp")
    print(ip_address)
    print(username)
    print(password)
    print(local_dir)
    print(remote_dir)
def download_from_ftp(ftp_server, ftp_user, ftp_password, remote_folder, local_folder):
    print("download_from_ftp")
    print(ftp_server)
    print(ftp_user)
    print(ftp_password)
    print(remote_folder)
    print(local_folder)
