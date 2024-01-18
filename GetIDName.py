import re

string = "192.168.3.4_3JF04_2051153147+庄雨萱"

# 提取数字部分
numbers = re.findall(r"\d+", string)
number = numbers[-1] if numbers else None

# 提取中文部分
chinese = re.findall(r"\+(\S+)", string)
chinese_text = chinese[0] if chinese else None

print("提取的数字部分:", number)
print("提取的中文部分:", chinese_text)
