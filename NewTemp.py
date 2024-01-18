import os

def get_subdirectories(folder_path):
    subdirectories = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
    return subdirectories

# 获取文件夹C的子目录列表Z
folder_path = "C:\\NCRE_KSWJJ\\班级"
subdirectories_list = get_subdirectories(folder_path)

# 打印子目录列表Z
for subdirectory in subdirectories_list:
    print(subdirectory)