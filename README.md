# Data_backup
数据备份课程设计

实现了完全备份差分备份和增量备份
网络备份使用ftp服务

数据恢复目前仅支持恢复当前备份的文件，不支持节点的回滚

使用命令行使用

例如

```
python main.py -C D:\\BaiduNetdiskDownload\\haizeiwang D:\\python\\backup_test5
main.py -U D:\\BaiduNetdiskDownload\\FlashBrowser_v1.0.5 remote --ip 10.142.248.81 --user li123 --pd 123456
# 使用--help获取更多信息
```

