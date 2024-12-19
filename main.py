import Backup as Bk
import os
import argparse
import test1 as t1


def command():
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description="备份程序：支持完全备份、差分备份和增量备份")
    # 添加参数
    parser.add_argument(
        '-C', '--complete',
        action='store_true',
        help="完全备份"
    )
    parser.add_argument(
        '-D', '--differential',
        action='store_true',
        help="差分备份"
    )
    parser.add_argument(
        '-I', '--incremental',
        action='store_true',
        help="增量备份"
    )
    parser.add_argument(
        "-U", "--update",
        action="store_true",
        help="上传到ftp服务器"
    )
    parser.add_argument(
        "-L", "--download",
        action="store_true",
        help="下载到本地"
    )
    parser.add_argument(
        "-R", "--restore",
        action="store_true",
        help="恢复数据"
    )
    parser.add_argument(
        'Source_path',
        help='源路径'
    )
    parser.add_argument(
        'Target_path',
        help='目标路径'
    )
    parser.add_argument(
        '--include',
        type=str,
        help="仅备份哪种文件",
        default=None
    )
    parser.add_argument(
        '--exclude',
        type=str,
        help="不备份指定文件",
        default=None
    )
    parser.add_argument(
        '--ip',
        type=str,
        help="网络备份时的ip地址",
        default=None
    )
    parser.add_argument(
        '--user',
        type=str,
        help="用户名",
        default=None
    )
    parser.add_argument(
        '--pd',
        type=str,
        help="密码",
        default=None
    )
    # 解析参数
    args = parser.parse_args()
    try:
        # 根据参数执行对应的功能
        if args.complete:
            Bk.complete_backup(args.Source_path, args.Target_path, args.include, args.exclude)
        elif args.differential:
            Bk.diff_backup(args.Source_path, args.Target_path)
        elif args.incremental:
            Bk.incremental_backup_call(args.Source_path, args.Target_path)
        elif args.restore:
            Bk.restore_backup(args.Source_path, args.Target_path)
        elif args.update:
            Bk.update_to_ftp(args.ip, args.user, args.pd, args.Source_path, args.Target_path)
        elif args.download:
            Bk.download_from_ftp(args.ip, args.user, args.pd, args.Source_path, args.Target_path)
        else:
            print("请选择一个备份模式（-C 或 -D 或 -I）")
    except ValueError as e:
        print("请检查您的输入" + e)


if __name__ == '__main__':
    command()
