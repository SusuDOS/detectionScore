# ################################################
# 功能描述:
#     1.检测所有文本文件名称格式是否合法.
#     2.合法，则比较所有文本文件内容与标准文件的编辑距离.
#     3.将所有的编辑距离以电子表格形式返回.
# ################################################

import os
import re
import Levenshtein
from openpyxl import Workbook

data = []

def check_file_names(folder_path="班级"):
    # 如果存在非法文件名返回False，否则返回True
    pattern = r'^\d+\+[\u4e00-\u9fff]+\.(txt|TXT)$'
    has_invalid_name = False  # 初始值，文件名称都合法!

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path) and filename.endswith(('.txt', '.TXT')):
            if not re.match(pattern, filename):
                has_invalid_name = True
                print(f"非法文件名: {filename}")
            else:
                print(f"合法文件名: {filename}")

    if has_invalid_name:
        print("检测不通过，存在非法文件名!\n")
    else:        
        print("检测通过，所有文件名均符合要求!\n")

    return not has_invalid_name


def write_to_excel(data):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["学号","姓名","出错数"])
    for row in data:
        sheet.append(row)
    workbook.save("学生打字成绩分析.xlsx")

def calculate_edit_distance(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    return distance

def search_text_documents(directory="班级", search_string=""):
    found_documents = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    row = []
                    print("*************")
                    print(file_path)
                    content = file.read()
                    edit_distance = calculate_edit_distance(content, search_string)
                    print("{} 的编辑距离为:{}".format(file_path,edit_distance))
                    num_name_kuozhan_array = file_path.split('\\')[1].split("+")
                    print(num_name_kuozhan_array)
                    row.append(num_name_kuozhan_array[0])
                    num_name_array = num_name_kuozhan_array[1].split(".")
                    row.append(num_name_array[0])
                    row.append(edit_distance)
                data.append(row)
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='ansi') as file:
                    row = []
                    print("*************")
                    print(file_path)
                    content = file.read()
                    edit_distance = calculate_edit_distance(content, search_string)
                    print("{} 的编辑距离为:{}".format(file_path,edit_distance))
                    num_name_kuozhan_array = file_path.split('\\')[1].split("+")
                    row.append(num_name_kuozhan_array[0])
                    num_name_array = num_name_kuozhan_array[1].split(".")
                    row.append(num_name_array[0])
                    row.append(edit_distance)
                data.append(row)       

    return found_documents

# 1.文件名称不合法,直接退出.
if not check_file_names():
    print("脚本已退出!")
    exit()

# 2.打开标准文件，进行对比.
with open("Standard.txt", encoding='utf-8') as file:
    content = file.read()
search_string = content

# 3.遍历每个文件，获取编辑距离.
results = search_text_documents("班级", search_string)
write_to_excel(data)

print("输出已保存到  学生打字成绩分析.xlsx  文件中！")