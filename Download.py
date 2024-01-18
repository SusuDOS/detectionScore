import requests
import os
import multiprocessing
import time

url = "https://tiantianfacai1.oss-ap-southeast-1.aliyuncs.com/yunduanxc.apk"
num_threads = 12  # 并发线程数
num_requests = 10000  # 总请求数
cleanup_interval = 10  # 清理间隔，单位：秒

def download_file(i):
    response = requests.get(url, stream=True)
    file_name = f"downloaded_file_{i}.apk"
    temp_file_name = f"temp_downloaded_file_{i}.apk"
    with open(temp_file_name, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    os.rename(temp_file_name, file_name)
    
    # 在这里处理下载的文件，可以重命名、移动或进行其他操作
    # 例如：os.rename(file_name, f"renamed_file_{i}.apk")

def cleanup_files():
    while True:
        time.sleep(cleanup_interval)
        files = [f for f in os.listdir() if f.startswith("downloaded_file")]
        for file in files:
            os.remove(file)

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=num_threads)
    for i in range(num_requests):
        pool.apply_async(download_file, (i,))
    
    cleanup_process = multiprocessing.Process(target=cleanup_files)
    cleanup_process.start()

    pool.close()
    pool.join()

    cleanup_process.terminate()
    cleanup_process.join()
