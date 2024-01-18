import re
import pyautogui
import time
from cnocr import CnOcr

# img_fp = 'temp.png'

# 替换为客户端程序A的实际窗口标题
window_title = "评分"
def adjust_window(window_title = "评分" ):
    # 激活窗口
    window = pyautogui.getWindowsWithTitle(window_title)[0]
    window.activate()
    # 调整窗口大小
    window.resizeTo(720, 640)
    window.moveTo(0, 0)
    time.sleep(1)
    pyautogui.click(x=200, y=55, clicks=1, button='left')
    
    # 留下计算分数的时间,可以分段测试一下.
    time.sleep(14)
    
    # 指定区域截图，将 x、y、width、height 替换为实际数值
    # 评分结束。本题满分10分，考生得分0分
    screenshot = pyautogui.screenshot(region=(285, 32, 315, 42))  

    # 将截图保存为临时文件（可选），调试时候可以开启!
    # screenshot.save(img_fp)
    return screenshot
    
def GetValue(screenshot):
    ocr = CnOcr()
    # out = ocr.ocr_for_single_line(img_fp)
    # out = ocr.ocr(img_fp)
    out = ocr.ocr(screenshot)

    # 本题满分10分，考生得分0分
    text_values = ''.join([item['text'] for item in out])

    print("检测到文本: ", text_values)
    numbers = re.findall(r'\d+\.\d+|\d+',text_values)

    assert len(numbers) == 2, "列表数值元素个数不为2,识别有问题，已退出!"
    print("数值:{}，得分:{}".format(numbers,numbers[-1]))
    
    # 置空，防止干扰.
    screenshot = None
    return numbers[-1]


# 调用函数调整窗口大小和移动窗口位置
num = GetValue(adjust_window())


print(num)
