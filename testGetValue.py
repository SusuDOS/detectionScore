import re
from cnocr import CnOcr

img_fp = 'temp.png'
ocr = CnOcr()
# out = ocr.ocr_for_single_line(img_fp)
out = ocr.ocr(img_fp)

# 本题满分10分，考生得分0分
text_values = ''.join([item['text'] for item in out])

print("检测到文本: ", text_values)
numbers = re.findall(r'\d+\.\d+|\d+',text_values)

assert len(numbers) == 2, "列表数值元素个数不为2,识别有问题，已退出!"
print("数值:{}，得分:{}".format(numbers,numbers[-1]))

