import pyautogui
import time

window_title = "评分"  # 替换为客户端程序A的实际窗口标题
def adjust_window(window_title):
    # 激活窗口
    window = pyautogui.getWindowsWithTitle(window_title)[0]
    window.activate()
    # 调整窗口大小
    window.resizeTo(720, 640)
    window.moveTo(0, 0)
    time.sleep(1)
    pyautogui.click(x=200, y=55, clicks=1, button='left')
    # 留下计算分数的时间
    time.sleep(10)
    # time.sleep(1)
    # 指定区域截图，将 x、y、width、height 替换为实际数值
    # 评分结束。本题满分10分，考生得分0分
    screenshot = pyautogui.screenshot(region=(285, 32, 315, 42))  

    # 将截图保存为临时文件（可选）
    screenshot.save('temp.png')  # 保存为文件，可以根据需要更改文件名和保存路径

    # 使用pytesseract进行图像中数字cls的识别

# 调用函数调整窗口大小和移动窗口位置
adjust_window(window_title)
