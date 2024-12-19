import datetime as dt
import os
import Backup as Bk
# 测试创建对应的时间文件夹有无错误
# now = dt.datetime.now()
# time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
# print(os.path.join("/root/home", time_str))

# 检测时间为文件夹的创建是否正确
# now = dt.datetime.now()
# time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
# Bk.mark("D:\\python\\Data_Backup", "C", time_str)

# 测试scan的功能
# bool_tmp = Bk.scan("D:\\python\\backup_test")
# print(bool_tmp)

# 测试diff_backup的功能
# Bk.diff_backup("D:\\BaiduNetdiskDownload\\haizeiwang", "D:\\python\\backup_test1")

# 测试get_file_metadata
# print(Bk.get_file_metadata("D:\\python\\backup_test1"))

# 测试增量备份的功能
# Bk.incremental_backup("D:\\BaiduNetdiskDownload\\haizeiwang", "D:\\python\\backup_test1")

# 测试数据恢复功能
# Bk.restore_backup("D:\\python\\backup_test1", "D:\\python\\backup_test3")

# 测试网络备份功能 上传到ftp服务器
# Bk.update_to_ftp("192.168.1.188", "li123", "123456", "D:\\BaiduNetdiskDownload\\FlashBrowser_v1.0.5", "remote")

# 从ftp服务器下载文件
# Bk.download_from_ftp("192.168.1.188", "li123", "123456", "remote", "D:\\python\\backup_test4")


