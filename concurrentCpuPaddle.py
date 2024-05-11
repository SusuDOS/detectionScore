import re
import os
import sys
import time
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
from paddleocr import PaddleOCR
from concurrent.futures import ProcessPoolExecutor
from natsort import natsorted


"""
CPU极慢需要使用多进程,无法多线程实现.

限定,其他版本未测试:
pip install paddlepaddle==2.4.2
"""


# 全局变量，用于存储 OCR 引擎实例
global_ocr_engine = None
finishedInfo = {}
finishedCount = {}

special_chars_pattern = re.compile(r'[，。！()#\s%@（）、【】\[\]]')
content_pattern = re.compile(r'^电子表格$|.成绩.*|^第\d{1,2}[\u4e00-\u9fff]$', re.IGNORECASE)
# 替换中文冒号
colon_pattern = re.compile(r'：')


# 排序:电子表格，第，总成绩
def custom_key(item):
    if "总成绩" in item:
        return 2
    elif "第" in item:
        return 1
    else:
        return 0


def has_chinese_and_english(text):    
    return re.search('[\u4e00-\u9fff]', text) and re.search('[a-zA-Z]', text)

def extract_id_name(filename):
    clean_path = re.sub(r'\s', '', filename)
    numbers = re.findall(r'\d{6,}', clean_path)
    chineses = re.findall(r'([\u4e00-\u9fa5]{1,3})', clean_path)
    return numbers[0] if numbers else None, chineses[0] if chineses else None

    
def init_ocr_engine(use_angle_cls=True, lang='ch',use_gpu=False):
    """ 初始化每个进程的 OCR 引擎 """
    global global_ocr_engine
    global_ocr_engine = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang, use_gpu = use_gpu)

def ocr_image(image_path):
    """ 使用全局 OCR 引擎处理单个图像 """
    # Debug: 打印进程ID
    print(f"Processing {image_path} on process {os.getpid()}")
    try:
        result = global_ocr_engine.ocr(image_path, cls=True)
        if(result[0]!=None):
            filtered_list = []        
            for item in result[0]:
                # 解包元组以简化代码
                text, confidence = item[1]
                if confidence > 0.8 and 3 <= len(text) <= 10:
                    # 清除特殊字符
                    cleaned_text = special_chars_pattern.sub('', text)                
                    if content_pattern.search(cleaned_text):
                        # 冒号改为英文冒号
                        cleaned_text = colon_pattern.sub(':', cleaned_text)
                        filtered_list.append(cleaned_text)
        
            # 结果排序:电子表格，第，总成绩
            sorted_lines_list = sorted(filtered_list, key=lambda x: custom_key(x))
            
            # 断言结果合法
            check_id_name_length(sorted_lines_list)
            return (image_path, sorted_lines_list)
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return (image_path, None)


def process_images(folder_path, use_angle_cls=True, lang='ch'):
    # 获取文件名称合法的图片
    image_paths = []
    for folder_path, _, filenames in os.walk(folder_path):
        for fname in filenames:
            if fname.lower().endswith(('.png', '.jpg', '.jpeg')) and has_chinese_and_english(fname):
                image_paths.append(os.path.join(folder_path, fname))

    with ProcessPoolExecutor(max_workers=os.cpu_count(), initializer=init_ocr_engine, initargs=(use_angle_cls, lang)) as executor:
        results = list(executor.map(ocr_image, image_paths))

    # 对结果按路径自然排序            
    return natsorted(results, key=lambda x: x[0])


def check_id_name_length(sorted_lines_list):
    try:
        # 断言检查id_name的长度是否为3，因为要输出字典需要检验数据.
        assert len(sorted_lines_list) == 3, "元素个数不对"
    except AssertionError as e:
        # 如果长度不正确，打印错误消息和id_name的详细信息，然后退出脚本
        print(e)
        print("id_name的信息:", sorted_lines_list)
        sys.exit(1)


def add_score(id_name, work_id, score):
    if id_name not in finishedInfo:
        finishedInfo[id_name] = {}
        finishedCount[id_name] = 0
    if work_id in finishedInfo[id_name]:
        finishedInfo[id_name][work_id] = max(finishedInfo[id_name][work_id], score)
    else:
        finishedInfo[id_name][work_id] = score
        finishedCount[id_name] += 1


def save_as_image(results, filename):
    # 结果预处理
    for image_path, sorted_lines_list in results:
        if sorted_lines_list is not None:
            student_id, student_name = extract_id_name(image_path)
            
            id_name = (student_id[-2:], student_name)
            add_score(id_name,(sorted_lines_list[0],sorted_lines_list[1]),sorted_lines_list[2])

        else:
            print(f"No results for {image_path} due to error.")        
    
    
    # 输出到图片
    items = natsorted(finishedInfo.items(), key=lambda x: x[0][0])

    # 设置图片大小
    submitted_count = len(items)
    counts = list(finishedCount.values())
    count_frequencies = Counter(counts)
    
    # 众数决定图片宽度和缺失作业个数.
    # 众数=真实的作业数量
    mode = max(count_frequencies, key=count_frequencies.get)
    
    
    # 最大数=优秀同学超额完成的量
    max_value = max(finishedCount.values())
    
    image = Image.new("RGB", (min(max_value*364+80,2560), submitted_count*84+100), color="white")
    draw = ImageDraw.Draw(image)
    
    # 查找缺失学号
    # 排序 ID 并找到第一个小于50的最大值
    sorted_ids = sorted([int(key[0]) for key in finishedCount.keys() if int(key[0]) < 50])
    if sorted_ids:
        max_id = sorted_ids[-1]
    else:
        max_id = 66
    
    # 确保生成的是两位数字符串，max_id:最大学号.
    all_ids = set(f"{i:02}" for i in range(1, max_id + 1))
    existing_ids = set(key[0] for key in finishedCount.keys())
    
    # 确定缺失的 ID，确保输出有序.
    missing_ids = natsorted(all_ids - existing_ids)
    submitted_count = len(finishedCount)
    unsubmittedInfo = len(missing_ids)
    

    # fc-list | grep -i simsun
    # 检测操作系统
    if os.name == 'nt':  # Windows系统
        font_path = "simsun.ttc"
    else:  # 默认为Unix/Linux系统
        font_path = "/usr/share/fonts/truetype/simsun/simsun.ttc"

    # 加载字体
    font = ImageFont.truetype(font_path, 16)
    
    x_margin = 64
    y_margin = 64
    
    for key, texts in items:
        text = f"学号:{key[0]}  姓名:{key[1]}   缺少:{max(mode - finishedCount[key],0)}"
        draw.text((x_margin, y_margin), text, font=font, fill="black")
        y_margin +=24

        text = f"提交信息:{texts}"
        draw.text((x_margin, y_margin), text, font=font, fill="black")
        y_margin +=48
        
    # 信息追加
    submittedInfo = f"\n\n\n作业提交人数：{submitted_count}\n\n"
    unsubmittedInfo = f"作业未提交人数：{unsubmittedInfo}\n{missing_ids}\n"

    runInfo = "\n\n\n任务完成，耗时：" + "{:.2f}".format(time.time()-startString) + "秒!\n"
    warnInfo = "\n警告：若提交信息不是从左往右递增，则说明格式必定错误！"

    combined_info = submittedInfo + unsubmittedInfo + runInfo + warnInfo
    draw.text((x_margin, y_margin), combined_info, font=font, fill="black")
    image.save(filename)
    

if __name__ == "__main__":
    startString = time.time()
    folder_path = "."
    results = process_images(folder_path)
    save_as_image(results,"resultPractice.png")
    print("\n任务完成，耗时：" + "{:.2f}".format(time.time()-startString) + "秒!\n")
