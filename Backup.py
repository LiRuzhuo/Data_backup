import os
import sys
import shutil
import datetime as dt
from ftplib import *

Cb = "Complete"
Db = "Different"
Ib = "Increment"


# 确定这个文件夹里有没有全量备份,(在差分备份和增量备份之前使用)
def scan(target_folder, mode):
    tmp_file = os.path.join(target_folder, mode + ".txt")
    if not os.path.exists(tmp_file):
        return False
    else:
        with open(tmp_file, "r") as file:
            mode_tmp = file.readline().split(",")
            if mode_tmp[0] != '':
                if mode_tmp[1] == mode:
                    return True
        return False


# 标记本次备份是全量备份还是差分备份还是增量备份
def mark(target_folder, mode, file_name):
    mark_file = os.path.join(target_folder, mode + ".txt")
    with open(mark_file, "a") as file:
        file.seek(0, 2)
        file.write(file_name + "," + mode + "," + "\n")


# 全量备份，获取时间作文备份文件夹的文件名
def complete_backup(source_folder, target_folder, filter_include=None, filter_exclude=None, show_progress=True):
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Source folder '{source_folder}' does not exist.")
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    if scan(target_folder, Cb):
        print("已有完全备份，请选择其他目录")
        return
    now = dt.datetime.now()
    time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    mark(target_folder, Cb, time_str)
    target_folder = os.path.join(target_folder, time_str)

    # 统计总文件数，用于显示进度条
    total_files = 0
    if filter_include:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_extension = os.path.splitext(file)[1]
                if filter_include and file_extension in filter_include:
                    total_files += 1
    elif filter_exclude:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_extension = os.path.splitext(file)[1]
                if filter_exclude and file_extension not in filter_exclude:
                    total_files += 1
    else:
        total_files = sum([len(files) for _, _, files in os.walk(source_folder)])
    processed_files = 0

    for root, dirs, files in os.walk(source_folder):
        # 获取当前的文件路径
        relative_path = os.path.relpath(root, source_folder)
        current_target_folder = os.path.join(target_folder, relative_path)

        # 如果目录不存在则创建目录
        if not os.path.exists(current_target_folder):
            os.makedirs(current_target_folder)

        for file in files:
            # 判断排除或者 ”仅“ 情况
            file_extension = os.path.splitext(file)[1]
            if filter_include and file_extension not in filter_include:
                continue
            if filter_exclude and file_extension in filter_exclude:
                continue
            # 使用root和file组成源文件路径和备份文件路径
            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(current_target_folder, file)
            # 复制文件
            shutil.copy2(source_file_path, target_file_path)

            processed_files += 1
            # 使用sys模块来显示进度条
            if show_progress:
                progress = (processed_files / total_files) * 100
                sys.stdout.write(f"\rProgress: {processed_files}/{total_files} files copied ({progress:.2f}%).")
                sys.stdout.flush()

    if show_progress:
        print(f"\nBackup completed. {processed_files} files copied.")


"""
差分备份
"""


# 获取目录中文件的相对路径及其最后修改时间
def get_file_metadata(directory):
    file_metadata = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            file_metadata[relative_path] = os.path.getmtime(file_path)
    return file_metadata


def diff_backup(source_folder, target_folder, mode=Db):
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Source folder '{source_folder}' does not exist.")
    if not os.path.exists(target_folder):
        print("目录不存在，请先创建全量备份或者选择正确的全量备份目录")
        return
    flag = False
    # 检测有没有全量备份，差分备份必须要一次全量备份才可以执行
    if not scan(target_folder, Cb):
        print("请先创建全量备份")
        return
    # 检测是否有差分备份，如果有就更新当前的差分备份的信息，如果无就新建
    elif scan(target_folder, mode):
        flag = True

    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Source folder '{source_folder}' does not exist.")

    # 删除上次的差分备份的文件
    if flag:
        with open(os.path.join(target_folder, mode + ".txt"), "r") as file:
            lines = file.readlines()
            last_line = lines[-1] if lines else ''
        tmp_line = last_line.split(",")
        del_path = os.path.join(target_folder, tmp_line[0])
        del_file = os.path.join(target_folder, tmp_line[0] + ".txt")

        if os.path.exists(del_path):
            shutil.rmtree(del_path)
        if os.path.exists(del_file):
            os.remove(del_file)

    # 获取全量备份的文件夹名称
    with open(os.path.join(target_folder, Cb + ".txt"), "r") as file:
        file_name = file.readline().split(",")[0]
    complete_filepath = os.path.join(target_folder, file_name)

    # 被删除的文件绝对路径
    now = dt.datetime.now()
    time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    deleted_files_path = os.path.join(target_folder, time_str + ".txt")
    dest_file_path = os.path.join(target_folder, time_str)

    # 获取源目录和完整备份目录的文件元数据
    source_metadata = get_file_metadata(source_folder)
    complete_metadata = get_file_metadata(complete_filepath)

    # 比较文件差异
    add_or_updated = {}
    deleted_files = []

    for file_path, mtime in source_metadata.items():
        if file_path not in complete_metadata:
            # 新增的文件情况
            add_or_updated[file_path] = "added"
        elif mtime > complete_metadata[file_path]:
            # 文件更新情况
            add_or_updated[file_path] = "updated"
    for file_path in complete_metadata:
        if file_path not in source_metadata:
            # 删除文件的情况
            deleted_files.append(file_path)

    if add_or_updated:
        # 复制新增和更新的文件
        for file_path, status in add_or_updated.items():
            src_path = os.path.join(source_folder, file_path)
            dest_path = os.path.join(dest_file_path, file_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)
            print(f"文件 {status}: {file_path}")

    if deleted_files:
        # 将删除的文件标记
        with open(deleted_files_path, "w") as file:
            for file_path in deleted_files:
                file.write(file_path + "\n")
                print(f"文件删除: {file_path}")
    if deleted_files or add_or_updated:
        # 写入日志
        mark(target_folder, mode, time_str)

    return 0


"""
增量备份部分
"""


def incremental_backup(source_folder, target_folder):
    if not os.path.exists(source_folder):
        raise FileNotFoundError(f"Source folder '{source_folder}' does not exist.")
    if not os.path.exists(target_folder):
        print("目录不存在，请先创建全量备份或者选择正确的全量备份目录")
        return

    # 检测有没有全量备份
    if not scan(target_folder, Cb):
        print("请先创建全量备份")
        return

    # 获取全量备份的文件夹名称
    with open(os.path.join(target_folder, Cb + ".txt"), "r") as file:
        file_name = file.readline().split(",")[0]

    # 被删除的文件绝对路径
    now = dt.datetime.now()
    time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    deleted_files_path = os.path.join(target_folder, time_str + ".txt")
    dest_file_path = os.path.join(target_folder, time_str)

    # 初始化文件列表
    file_list = [file_name]
    with open(os.path.join(target_folder, Ib + ".txt"), "r") as file:
        for line in file:
            file_list.append(line.split(",")[0])
    # 依次获取元数据
    source_metadata = get_file_metadata(source_folder)
    incremental_metadata = {}
    for i in file_list:
        file_metadata = get_file_metadata(os.path.join(target_folder, i))
        incremental_metadata.update(file_metadata)
        del_files = []  # 被删除的文件列表
        del_file_path = os.path.join(target_folder, i + ".txt")
        if not os.path.exists(del_file_path):
            continue
        with open(del_file_path, "r") as file:
            for line in file:
                del_files.append(line.strip())
        for j in del_files:
            incremental_metadata.pop(j)

    # 比较文件差异
    add_or_updated = {}
    deleted_files = []

    for file_path, mtime in source_metadata.items():
        if file_path not in incremental_metadata:
            # 新增的文件情况
            add_or_updated[file_path] = "added"
        elif mtime > incremental_metadata[file_path]:
            # 文件更新情况
            add_or_updated[file_path] = "updated"
    for file_path in incremental_metadata:
        if file_path not in source_metadata:
            # 删除文件的情况
            deleted_files.append(file_path)
    if add_or_updated:
        # 复制新增和更新的文件
        for file_path, status in add_or_updated.items():
            src_path = os.path.join(source_folder, file_path)
            dest_path = os.path.join(dest_file_path, file_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)
            print(f"文件 {status}: {file_path}")
    if deleted_files:
        # 将删除的文件标记
        with open(deleted_files_path, "w") as file:
            for file_path in deleted_files:
                file.write(file_path + "\n")
                print(f"文件删除: {file_path}")
    if deleted_files or add_or_updated:
        # 写入日志
        mark(target_folder, Ib, time_str)

    return 0


"""
数据恢复部分
"""


def find_backup_files(backup_folder, mode):
    """找到指定模式的备份记录"""
    marker_file = os.path.join(backup_folder, f"{mode}.txt")
    if not os.path.exists(marker_file):
        return []
    with open(marker_file, "r") as file:
        backups = [line.split(",")[0] for line in file.readlines()]
    return backups


def restore_backup(target_folder, restore_folder):
    """恢复全量、差分或增量备份"""
    if not os.path.exists(target_folder):
        print("备份目录不存在，请检查路径")
        return

    # 创建恢复目标目录
    if not os.path.exists(restore_folder):
        os.makedirs(restore_folder)

    # 获取全量备份记录
    complete_backups = find_backup_files(target_folder, Cb)
    if not complete_backups:
        print("未找到全量备份，无法进行恢复")
        return

    # 恢复全量备份
    latest_complete_backup = os.path.join(target_folder, complete_backups[0])
    print(f"恢复全量备份：{latest_complete_backup}")
    copy_files(latest_complete_backup, restore_folder)

    # 获取差异备份记录
    diff_backups = find_backup_files(target_folder, Db)
    if diff_backups:
        print("应用差异备份...")
        apply_backup_files(target_folder, diff_backups[-1], restore_folder)

    # 获取增量备份记录
    increment_backups = find_backup_files(target_folder, Ib)
    if increment_backups:
        print("应用增量备份...")
        for increment_backup in increment_backups:
            apply_backup_files(target_folder, increment_backup, restore_folder)

    print("数据恢复完成！")


def copy_files(source_folder, destination_folder):
    """将源文件夹中的所有文件复制到目标文件夹"""
    for root, _, files in os.walk(source_folder):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, source_folder)
            dest_path = os.path.join(destination_folder, rel_path, file)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(src_path, dest_path)


def apply_backup_files(target_folder, backup_name, restore_folder):
    """应用差异或增量备份"""
    backup_folder = os.path.join(target_folder, backup_name)
    deleted_files_file = os.path.join(target_folder, backup_name + ".txt")

    # 复制新增和更新的文件
    print(f"应用备份文件：{backup_folder}")
    copy_files(backup_folder, restore_folder)

    # 删除标记的已删除文件
    if os.path.exists(deleted_files_file):
        with open(deleted_files_file, "r") as file:
            deleted_files = [line.strip() for line in file.readlines()]
        for deleted_file in deleted_files:
            file_path = os.path.join(restore_folder, deleted_file)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除文件：{file_path}")


"""
网络备份
"""


def update_to_ftp(ip_address, username, password, local_dir, remote_dir):
    ftp = FTP()
    try:
        ftp.connect(ip_address)
        ftp.login(username, password)
    except ConnectionError:
        print("无法连接到服务器")
        return

    # 递归复制文件
    def upload_directory(local_path, remote_path):
        if remote_dir not in ftp.nlst():
            ftp.mkd(remote_path)
        ftp.cwd(remote_path)
        for item in os.listdir(local_path):
            local_path_tmp = os.path.join(local_path, item)
            if os.path.isdir(local_path_tmp):
                upload_directory(local_path_tmp, item)
                ftp.cwd("..")
            else:
                print(f"上传文件:{local_path_tmp}")
                with open(local_path_tmp, "rb") as file:
                    ftp.storbinary(f"STOR {item}", file)

    upload_directory(local_dir, remote_dir)
    ftp.quit()
    print(f"文件已经备份到:{ip_address}/{remote_dir}")

def download_from_ftp(ftp_server, ftp_user, ftp_password, remote_folder, local_folder):
    """
    从 FTP 服务器下载备份文件
    """
    ftp = FTP()
    try:
        ftp.connect(ftp_server)
        ftp.login(ftp_user, ftp_password)
    except Exception as e:
        print(f"无法连接到 FTP 服务器: {e}")
        return

    def download_directory(remote_dir, local_dir):
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        ftp.cwd(remote_dir)
        for item in ftp.nlst():
            if is_directory(ftp, item):  # 如果是文件夹
                download_directory(item, os.path.join(local_dir, item))
                ftp.cwd("..")
            else:  # 如果是文件
                local_path = os.path.join(local_dir, item)
                print(f"下载文件:{local_path}")
                with open(local_path, "wb") as f:
                    ftp.retrbinary(f"RETR {item}", f.write)

    download_directory(remote_folder, local_folder)
    ftp.quit()
    print(f"备份文件已从 FTP 服务器下载到: {local_folder}")


def is_directory(ftp, path):
    try:
        ftp.cwd(path)
        ftp.cwd("..")
        return True  # 是目录
    except error_perm as e:
        if '550' in str(e):  # 检查错误码是否为550
            return False  # 不是目录，可能是文件或路径不存在
        else:
            raise

def incremental_backup_call(source_folder, target_folder):
    if scan(target_folder, Ib):
        incremental_backup(source_folder, target_folder)
    else:
        diff_backup(source_folder, target_folder, Ib)
    return
