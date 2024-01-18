import os
import shutil

def try_remove(file_path):
    try:
        os.remove(file_path)
        return True
    except OSError as e:
        print(f"删除文件报错:{file_path}: {e}")
        return False

def try_rmtree(folder_path):
    try:
        shutil.rmtree(folder_path)
        return True
    except OSError as e:
        print(f"删除文件夹报错:{folder_path}: {e}")
        return False

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            if not try_remove(file_path):
                os.chmod(file_path, 0o777)
                try_remove(file_path)
        elif os.path.isdir(file_path):
            # 递归调用 clear_folder 删除子文件夹中的内容
            clear_folder(file_path)
            if not try_rmtree(file_path):
                os.chmod(file_path, 0o777)
                try_rmtree(file_path)

if __name__ == "__main__":
    folder_path = "C:\\NCRE_KSWJJ\\1570999999010101"
    clear_folder(folder_path)
