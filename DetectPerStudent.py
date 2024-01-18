import time
import re
import pyautogui
from cnocr import CnOcr
from openpyxl import Workbook
import os
import shutil
import ctypes
import warnings

warnings.filterwarnings('ignore', message='The default value of the antialias parameter')

def write_to_excel(data):
    workbook = Workbook()
    sheet = workbook.active
    # columns = ["学号", "姓名", "出错数", "基础操作", "WORD", "EXCEL", "PPT"]
    sheet.append(["学号","姓名","PPT"])
    for row in data:
        sheet.append(row)
    workbook.save("学生PPT分数.xlsx")

def get_subdirectories(folder_path):
    subdirectories = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subdirectories.append(item_path)
    return subdirectories

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.chmod(file_path, 0o777)  # 修改文件权限为可写
            os.remove(file_path)
        elif os.path.isdir(file_path):
            clear_folder(file_path)  # 递归调用 clear_folder 删除子文件夹中的内容
            os.rmdir(file_path)

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
            attributes = ctypes.windll.kernel32.GetFileAttributesW(source_item)
            ctypes.windll.kernel32.SetFileAttributesW(destination_item, attributes)

def adjust_window(window_title = "评分"):
    window = pyautogui.getWindowsWithTitle(window_title)[0]
    window.activate()
    window.resizeTo(720, 640)
    window.moveTo(0, 0)
    time.sleep(1)
    pyautogui.click(x=200, y=55, clicks=1, button='left')
    pyautogui.click(x=200, y=55, clicks=1, button='left')
    # 合适的运行时间: 4 13 8 8
    # columns = "基础操作", "WORD", "EXCEL", "PPT"
    time.sleep(8)
    screenshot = pyautogui.screenshot(region=(285, 32, 315, 42))  
    return screenshot

def GetValue(screenshot):
    ocr = CnOcr()
    out = ocr.ocr(screenshot)
    text_values = ''.join([item['text'] for item in out])
    print("检测到文本: ", text_values)
    text_values = text_values.replace(',', '.').replace('，', '.')
    print("修正后: ", text_values)
    numbers = re.findall(r'\d+\.\d+|\d+',text_values)
    assert len(numbers) == 2, "列表数值元素个数不为2,识别有问题,已退出!"
    return numbers[-1]

def main():
    data = []
    target_folder = "C:\\NCRE_KSWJJ\\1570999999010101"
    clear_folder(target_folder)
    time.sleep(1)
    folder_path = "C:\\Users\\Administrator\\Desktop\\TestCheck\\班级"
    subdirectories_list = get_subdirectories(folder_path)
    window_title = "评分"
    for subdirectory in subdirectories_list:
        row = []
        clear_folder(target_folder)
        time.sleep(1)
        source_folder = subdirectory
        numbers = re.findall(r"\d+", subdirectory)
        number = numbers[-1] if numbers else None
        chinese = re.findall(r"\+(\S+)", subdirectory)
        chinese_text = chinese[0] if chinese else None
        copy_folder_contents(source_folder, target_folder)
        time.sleep(1)
        print("*"*40)
        print("学号:", number)
        print("姓名:", chinese_text)
        score = GetValue(adjust_window())
        print("得分:", score)
        print("")
        row.append(number)
        row.append(chinese_text)
        row.append(score)
        data.append(row)

    write_to_excel(data)

if __name__ == "__main__":
    main()
