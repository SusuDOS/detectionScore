import re
import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from cnocr import CnOcr
from collections import Counter

# 文字识别
class ImageTextProcessor:
    # 初始化变量
    def __init__(self, directory='.', extensions=('.jpg', '.jpeg', '.png', '.bmp')):
        self.directory = directory
        self.extensions = extensions
        self.ocr_engine = CnOcr()
        self.aggregated_data = {}
        self.finished_data = {}
        self.image_files = []
        self.start_time = time.time()
        self.special_chars_pattern = re.compile(r'[，,。！,()\s#%@()（）、 【】\[\]]')
        self.number_pattern = re.compile(r'\d{6,}')
        self.content_pattern = re.compile(r'.*电子表格.*|.*总成绩.*|^第\s*\d{1,2}', re.IGNORECASE)

    
    # 递归获取python脚本所在文件夹下的所有图片文件
    def find_images(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if file.lower().endswith(self.extensions):
                    self.image_files.append(os.path.join(root, file))
            
    
    # 处理文件夹下的图片
    def process_images(self):
        self.image_files = sorted(self.image_files, key=self.apply_natural_sort)
        self.submitted_count, self.missing_count, self.missing_students, self.most_common_submission_count = self.analyze_submissions()
        
        for image_file in self.image_files:
            student_number, student_name = self.extract_identifiers(image_file)
            if student_number is None or student_name is None:
                continue
            self.extract_text_from_image(image_file, student_number, student_name)
        
        self.print_aggregated_results()


    # 图片文件自然排序
    def apply_natural_sort(self, text):
        atoi = lambda text: int(text) if text.isdigit() else text
        return [atoi(c) for c in re.split(r'(\d+)', text)]


    # 分析图片文件情况
    def analyze_submissions(self):
        numbers = [re.search(self.number_pattern, file).group()[-2:] for file in self.image_files if re.search(self.number_pattern, file)]
        number_counter = Counter(numbers)
        max_number = max(map(int, numbers))
        
        # 学号有效性
        if max_number > 60:
            max_number = max(filter(lambda x: x <= 60, map(int, numbers)))
        all_possible_numbers = ['{:02d}'.format(num) for num in range(1, max_number + 1)]
        missing_numbers = sorted(set(all_possible_numbers) - set(numbers))
        submitted_count = len(set(numbers))
        missing_count = len(missing_numbers)
        count_frequencies = Counter(number_counter.values())
        most_common_submission_count = count_frequencies.most_common(1)[0][0]
        return submitted_count, missing_count, missing_numbers, most_common_submission_count

    
    # 获取文件名中的学号，名字
    def extract_identifiers(self, filename):
        clean_path = re.sub(r'\s', '', filename)
        numbers = re.findall(r'\d{6,}', clean_path)
        chineses = re.findall(r'([\u4e00-\u9fa5]{1,3})', clean_path)
        return numbers[0] if numbers else None, chineses[0] if chineses else None

    
    # 获取图片中的文字
    def extract_text_from_image(self, img, student_number, student_name):
        out = self.ocr_engine.ocr(img)
        
        # 初步筛选长度[3,30]，清理特殊字符.
        text_info = [item['text'] for item in out if 3 <= len(item['text']) < 30]
        cleaned_text_info = [self.special_chars_pattern.sub('', line) for line in text_info]
        
        # 查找满足规则的内容.
        filtered_lines_list = list(filter(lambda line: self.content_pattern.match(line), cleaned_text_info))

        # 连续的内容分开
        new_lines_list = []
        for line in filtered_lines_list:
            if len(line) > 7 and '第' in line:
                parts = line.split('第', 1)
                new_lines_list.append(parts[0])
                new_lines_list.append('第' + parts[1])
            else:
                new_lines_list.append(line)

        # 第6街->第6套
        pattern = re.compile(r'^第\s*\d{1,2}', re.IGNORECASE)
        processed_lines = []
        for line in new_lines_list:
            if pattern.match(line) and len(line) < 5:
                line = line[:-1] + '套'
            processed_lines.append(line)

        # 跳过 '批改' or '知识'
        filtered_lines_list = [line for line in processed_lines if '批改' not in line and '知识' not in line]
        
        # 排序输出
        sorted_lines_list = sorted(filtered_lines_list, key=lambda x: self.custom_key(x))
        
        key = (student_number[-2:], student_name)
        if key in self.aggregated_data:
            self.aggregated_data[key].extend(sorted_lines_list)
            self.finished_data[key] += 1
        else:
            self.aggregated_data[key] = sorted_lines_list
            self.finished_data[key] = 1

    
    # 排序:电子表格，第，总成绩
    def custom_key(self, item):
        if "总成绩" in item:
            return 2
        elif "第" in item:
            return 1
        else:
            return 0
        
        
    # 显示结果
    def print_aggregated_results(self):
        for key, texts in sorted(self.aggregated_data.items(), key=lambda x: x[0][0]):
            print(f"学号:{key[0]}  姓名:{key[1]}   缺少:{max(self.most_common_submission_count - self.finished_data[key],0)}\n提交信息:{texts}\n")
        print("已提交人数：", self.submitted_count)
        print("未提交人数：", self.missing_count)
        print("未提交学号：", self.missing_students)
        print("\n任务完成，耗时：", "{:.2f}".format(time.time() - self.start_time), "seconds!")
        print("\n警告：若提交信息不是从左往右递增，则说明格式必定错误！")
        


# 输出为图片
class PrintCapture:
    def __init__(self):
        self.output = ""

    def write(self, text):
        self.output += text

    def save_as_image(self, filename,submitted_count,most_common_count):
        # Create an image        
        image = Image.new("RGB", (min(most_common_count*360+100,2560), (submitted_count+1)*91+100), color="white")
        draw = ImageDraw.Draw(image)

        # font = ImageFont.truetype("simsun.ttc", 16)
        # fc-list | grep -i simsun
        font = ImageFont.truetype("/usr/share/fonts/truetype/simsun/simsun.ttc", 16)

        # Wrap text and draw on image
        lines = self.output.split("\n")
        
        x_margin = 64
        y_margin = 64
        
        for line in lines:
            draw.text((x_margin, y_margin), line, font=font, fill="black")
            y_margin += 28

        image.save(filename)
    def flush(self):
        pass
    
        
if __name__ == "__main__":    
    print("开始处理，预计2分钟...")
    image_processor = ImageTextProcessor()
    
    # 获取图片文件
    image_processor.find_images()
    
    # 获取文件的人数，任务个数，但不会影响缺失作业数量.
    submitted_count, missing_count, missing_numbers, most_common_count = image_processor.analyze_submissions()    
    
    # 开始捕获输出
    capture = PrintCapture()
    sys.stdout = capture

    # 图片文字处理
    image_processor.process_images()
    
    sys.stdout = sys.__stdout__
    
    # 图片保存
    capture.save_as_image("resultPractice.png",submitted_count,most_common_count)
    print("\n任务完成，耗时：", "{:.2f}".format(time.time() - image_processor.start_time), "seconds!")