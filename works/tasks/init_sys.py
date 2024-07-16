import sys
import os

def init():
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 将顶级包目录添加到 sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '../../')))