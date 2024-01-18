from openpyxl import Workbook

def write_to_excel(data):
    # 创建一个新的Excel工作簿
    workbook = Workbook()

    # 获取默认的工作表
    sheet = workbook.active

    # 逐行写入数据
    for row in data:
        sheet.append(row)

    # 保存Excel文件
    workbook.save("output.xlsx")

# 要输出到Excel的数据（假设是二维列表）
# 使用循环逐行构建二维列表
data = []
for i in range(3):
    row = []
    for j in range(3):
        row.append(i * 3 + j + 1)
    data.append(row)

print(data)


# 调用函数将数据写入Excel文件
write_to_excel(data)

print("输出已保存到output.xlsx文件。")
