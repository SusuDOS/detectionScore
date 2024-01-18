import os
import shutil
import ctypes

def copy_folder_contents(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        destination_item = os.path.join(destination_folder, item)

        if os.path.isdir(source_item):
            copy_folder_contents(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)
            # 获取原文件的隐藏属性
            attributes = ctypes.windll.kernel32.GetFileAttributesW(source_item)
            # 设置目标文件的隐藏属性
            ctypes.windll.kernel32.SetFileAttributesW(destination_item, attributes)


# 示例用法
source_folder = "C:\\Users\\GaoMing\\Desktop\TestCheck\\班级\\192.168.2.46_2JF46_2050451152+张雄辉"
destination_folder = "D:\\NCRE_KSWJJ\\1568999999010101"

copy_folder_contents(source_folder, destination_folder)
