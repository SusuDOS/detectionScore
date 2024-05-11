import re
import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
from paddleocr import PaddleOCR
from natsort import natsorted
from collections import Counter

"""
GPU运行,CPU极慢需要使用多线程的脚本.

限定,其他版本未测试:
pip install paddlepaddle==2.4.2
"""

# 文字识别
class ImageTextProcessor:
    # 初始化变量
    def __init__(self, directory='.', extensions=('.jpg', '.jpeg', '.png', '.bmp')):
        self.directory = directory
        self.extensions = extensions
        
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True)

        self.finishedInfo = {}
        self.finishedCount = {}
        self.image_files = []
        self.start_time = time.time()

        self.special_chars_pattern = re.compile(r'[，。！()#\s%@（）、【】\[\]]')
        self.number_pattern = re.compile(r'\d{6,}')
        self.content_pattern = re.compile(r'^电子表格$|.成绩.*|^第\d{1,2}[\u4e00-\u9fff]$', re.IGNORECASE)
        self.colon_pattern = re.compile(r'：')


    def has_chinese_and_english(self, text):    
        return re.search('[\u4e00-\u9fff]', text) and re.search('[a-zA-Z]', text)

    
    # 递归获取python脚本所在文件夹下的合法图片文件
    def find_images(self):                    
        for folder_path, _, filenames in os.walk(self.directory):
            for fname in filenames:
                if fname.lower().endswith(self.extensions) and self.has_chinese_and_english(fname):
                    self.image_files.append(os.path.join(folder_path, fname))
            

    # 处理文件夹下的图片
    def process_images(self):
        self.image_files = natsorted(self.image_files)
        for image_file in self.image_files:
            student_number, student_name = self.extract_id_name(image_file)
            if student_number is None or student_name is None:
                continue
            self.ocr_image(image_file, student_number, student_name)

    
    # 获取文件名中的学号，名字
    def extract_id_name(self, filename):
        clean_path = re.sub(r'\s', '', filename)
        numbers = re.findall(r'\d{6,}', clean_path)
        chineses = re.findall(r'([\u4e00-\u9fa5]{1,3})', clean_path)
        return numbers[0] if numbers else None, chineses[0] if chineses else None

    
    # 获取图片中的文字
    def ocr_image(self, img, student_number, student_name):
        result = self.ocr_engine.ocr(img, cls=True)
        
        if(result[0]!=None):
            """百度识图输出格式:
            元组数据类型：(文本信息,置信度) = result[0][idx][1]
            """
            filtered_list = []        
            for item in result[0]:
                # 解包元组以简化代码
                text, confidence = item[1]
                if confidence > 0.8 and 3 <= len(text) <= 10:
                    # 清除特殊字符
                    cleaned_text = self.special_chars_pattern.sub('', text)                
                    if self.content_pattern.search(cleaned_text):
                        # 冒号改为英文冒号
                        cleaned_text = self.colon_pattern.sub(':', cleaned_text)
                        filtered_list.append(cleaned_text)
        
            # 结果排序:电子表格，第，总成绩
            sorted_lines_list = sorted(filtered_list, key=lambda x: self.custom_key(x))

            id_name = (student_number[-2:], student_name)
            self.check_id_name_length(sorted_lines_list)
            
            self.add_score(id_name,(sorted_lines_list[0],sorted_lines_list[1]),sorted_lines_list[2])


    def check_id_name_length(self, sorted_lines_list):
        try:
            # 断言检查id_name的长度是否为3，因为要输出字典需要检验数据.
            assert len(sorted_lines_list) == 3, "元素个数不对"
        except AssertionError as e:
            # 如果长度不正确，打印错误消息和id_name的详细信息，然后退出脚本
            print(e)
            print("id_name的信息:", sorted_lines_list)
            sys.exit(1)


    # 添加成绩信息,针对重复提交.
    def add_score(self, id_name, work_id, score):
        if id_name not in self.finishedInfo:
            self.finishedInfo[id_name] = {}
            self.finishedCount[id_name] = 0
        if work_id in self.finishedInfo[id_name]:
            self.finishedInfo[id_name][work_id] = max(self.finishedInfo[id_name][work_id], score)
        else:
            self.finishedInfo[id_name][work_id] = score
            self.finishedCount[id_name] += 1
            

    
    # 排序:电子表格，第，总成绩
    def custom_key(self, item):
        if "总成绩" in item:
            return 2
        elif "第" in item:
            return 1
        else:
            return 0
        

    def save_as_image(self, filename):
            # 排序数据
            items = sorted(self.finishedInfo.items(), key=lambda x: x[0][0])

            # 查找缺失学号
            # 排序 ID 并找到第一个小于50的最大值.
            sorted_ids = sorted([int(key[0]) for key in self.finishedCount.keys() if int(key[0]) < 50])
            if sorted_ids:
                max_id = sorted_ids[-1]
            else:
                max_id = 66
            
            # 确保生成的是两位数字符串,max_id：最大学号.
            all_ids = set(f"{i:02}" for i in range(1, max_id + 1))
            existing_ids = set(key[0] for key in self.finishedCount.keys())
            
            # 确定缺失的 ID，确保输出有序.
            missing_ids = natsorted(all_ids - existing_ids)
            submitted_count = len(self.finishedCount)
            unsubmitted_count = len(missing_ids)

            # 设置图片大小
            counts = list(self.finishedCount.values())
            count_frequencies = Counter(counts)
    
            # 众数决定图片宽度和缺失作业个数.
            # 众数=真实的作业数量
            mode = max(count_frequencies, key=count_frequencies.get)
            
            # 最大数=优秀同学超额完成的量
            max_value = max(self.finishedCount.values())
            
            image = Image.new("RGB", (min(max_value*364+80,2560), submitted_count*82+100), color="white")
            draw = ImageDraw.Draw(image)
            
            # 系统字体位置切换
            # fc-list | grep -i simsun
            if os.name == 'nt':
                font_path = "simsun.ttc"
            else:
                font_path = "/usr/share/fonts/truetype/simsun/simsun.ttc"
            font = ImageFont.truetype(font_path, 16)
            x_margin = 64
            y_margin = 64
            
            for key, texts in items:
                text = f"学号:{key[0]}  姓名:{key[1]}  完成数:{self.finishedCount[key]}  缺少:{max(mode - self.finishedCount[key],0)}"
                draw.text((x_margin, y_margin), text, font=font, fill="black")
                y_margin +=24

                text = f"提交信息:{texts}"
                draw.text((x_margin, y_margin), text, font=font, fill="black")
                y_margin +=48
                
            # 信息追加
            submittedInfo = f"\n\n\n作业提交人数：{submitted_count}\n\n"
            unsubmittedInfo = f"作业未提交人数：{unsubmitted_count}\n{missing_ids}\n"

            runInfo = "\n\n\n任务完成，耗时：" + "{:.2f}".format(time.time()-self.start_time) + "秒!\n"
            warnInfo = "\n警告：若提交信息不是从左往右递增，则说明格式必定错误！"

            combined_info = submittedInfo + unsubmittedInfo + runInfo + warnInfo
            draw.text((x_margin, y_margin), combined_info, font=font, fill="black")
            image.save(filename)

    
    def flush(self):
        pass

        
if __name__ == "__main__":
    image_processor = ImageTextProcessor()
    
    # 获取图片文件
    image_processor.find_images()    

    # 图片文字处理
    image_processor.process_images()    
    
    # 图片保存
    image_processor.save_as_image("resultPractice.png")
    print("\n任务完成，耗时：", "{:.2f}".format(time.time() - image_processor.start_time), "秒!")
    print("\n警告：若提交信息不是从左往右递增，则说明格式必定错误！")