import time
import re
import pyautogui
import time
from cnocr import CnOcr
import Levenshtein
from openpyxl import Workbook
import os
import shutil
import ctypes
import warnings

# 关闭特定警告
warnings.filterwarnings('ignore', message='The default value of the antialias parameter')


data = []

def write_to_excel(data):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["学号","姓名","PPT分数"])
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
            # 获取原文件的隐藏属性
            attributes = ctypes.windll.kernel32.GetFileAttributesW(source_item)
            # 设置目标文件的隐藏属性
            ctypes.windll.kernel32.SetFileAttributesW(destination_item, attributes)

# 清空目标文件夹
target_folder = 'D:\\NCRE_KSWJJ\\1568999999010101\\'
clear_folder(target_folder)
time.sleep(2)  # 休眠2秒钟

# 调用函数复制文件夹内容
# 拆文件夹，以子文件目录为结构
folder_path = "C:\\Users\GaoMing\Desktop\\TestCheck\\班级"
subdirectories_list = get_subdirectories(folder_path)


window_title = "评分"  # 替换为客户端程序A的实际窗口标题
def adjust_window(window_title):
    # 激活窗口
    window = pyautogui.getWindowsWithTitle(window_title)[0]
    window.activate()
    # 调整窗口大小
    window.resizeTo(900, 720)
    window.moveTo(0, 0)
    time.sleep(1)
    pyautogui.click(x=90, y=50, clicks=1, button='left')
    # 留下计算分数的时间
    time.sleep(3)
    # 指定区域截图，将 x、y、width、height 替换为实际数值
    screenshot = pyautogui.screenshot(region=(420, 32, 100, 40))  

    # 将截图保存为临时文件（可选）
    screenshot.save('temp.png')  # 保存为文件，可以根据需要更改文件名和保存路径

    # 使用pytesseract进行图像中数字的识别

# 调用函数调整窗口大小和移动窗口位置
adjust_window(window_title)

for subdirectory in subdirectories_list:
    row = []
    clear_folder(target_folder)
    time.sleep(1)  # 休眠2秒钟
    source_folder = subdirectory
    # C:\Users\GaoMing\Desktop\TestCheck\班级\192.168.3.12_3JF12_2051153110+龚华婷
    # print(subdirectory)
    
    # 提取数字部分
    numbers = re.findall(r"\d+", subdirectory)
    number = numbers[-1] if numbers else None

    # 提取中文部分
    chinese = re.findall(r"\+(\S+)", subdirectory)
    chinese_text = chinese[0] if chinese else None
    
    copy_folder_contents(source_folder, target_folder)
    time.sleep(1)  # 休眠2秒钟
    print("学号:", number)
    print("姓名:", chinese_text)
    # print("")
    
    
    ### 刷新分数##    
    pyautogui.click(x=90, y=50, clicks=1, button='left')
    # 留下计算分数的时间
    time.sleep(5)
    # 指定区域截图，将 x、y、width、height 替换为实际数值
    screenshot = pyautogui.screenshot(region=(420, 32, 100, 40)) 
    # 将截图保存为临时文件（可选）
    screenshot.save('temp.png')  # 保存为文件，可以根据需要更改文件名和保存路径
    time.sleep(1)  # 休眠2秒钟
    
    ## 分数识别 ##
    img_fp = 'temp.png'
    ocr = CnOcr()
    out = ocr.ocr(img_fp)
    # out = ocr.ocr(img_fp)
    # print(out["text"])
    scores = re.findall(r'\d+\.\d+|\d+', out[0]["text"])
    print("得分:", scores[0])
    print("")
    
    ## 存到分数到列表里面，再写入到电子表格.
    row.append(number)
    row.append(chinese_text)
    row.append(scores[0])
    data.append(row)

# 写入到电子表格
write_to_excel(data)   
