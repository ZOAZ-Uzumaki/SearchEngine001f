import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

MAX_FILE_SIZE = 1000000  # Максимальний розмір файлу (в байтах)
MAX_FILE_SUFFIX = 1  # Початковий суфікс для нових файлів

def check_image_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=headers)
        response = urlopen(req)
        return True
    except (URLError, HTTPError):
        return False

def create_new_file(file_path):
    directory = os.path.dirname(file_path)
    base_name, extension = os.path.splitext(os.path.basename(file_path))
    new_file_path = os.path.join(directory, f"{base_name}_{MAX_FILE_SUFFIX}{extension}")

    while os.path.exists(new_file_path):
        MAX_FILE_SUFFIX += 1
        new_file_path = os.path.join(directory, f"{base_name}_{MAX_FILE_SUFFIX}{extension}")

    return new_file_path

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        url = ""
        description = ""
        image_urls = []
        video_url = ""

        for line in f:
            line = line.strip()
            if line.startswith("https://") or line.startswith("http://"):
                url = line
            elif line.startswith("ALT:"):
                description = line[4:]
            elif line.startswith("Посилання:"):
                image_urls.append(line[10:])
            elif line.startswith("Відео:"):
                video_url = line[7:]

        if not url.startswith("https://") and not url.startswith("http://"):
            url = "http://" + url

        try:
            response = urlopen(url)
            print(f"Домен доступний: {url}")
        except (URLError, HTTPError) as e:
            print(f"Помилка доступу до домену: {url}")
            return

        with open("DataBase001T.txt", "a", encoding="utf-8") as output_file:
            if output_file.tell() > MAX_FILE_SIZE:
                new_file_path = create_new_file(file_path)
                print(f"Досягнуто максимальний розмір файлу. Створено новий файл: {new_file_path}")
                output_file.close()
                with open(new_file_path, "a", encoding="utf-8") as new_output_file:
                    new_output_file.write(f"URL: {url}\n")
                    new_output_file.write(f"Description: {description}\n")
                    for image_url in image_urls:
                        if not image_url.startswith("https://") and not image_url.startswith("http://"):
                            image_url = url + image_url
                        image_url = quote(image_url, safe=':/')
                        if check_image_url(image_url):
                            new_output_file.write(f"Image URL: {image_url} (Accessible)\n")
                        else:
                            new_output_file.write(f"Image URL: {image_url} (Inaccessible)\n")
                    new_output_file.write(f"Video URL: {video_url}\n\n")
            else:
                output_file.write(f"URL: {url}\n")
                output_file.write(f"Description: {description}\n")
                for image_url in image_urls:
                    if not image_url.startswith("https://") and not image_url.startswith("http://"):
                        image_url = url + image_url
                    image_url = quote(image_url, safe=':/')
                    if check_image_url(image_url):
                        output_file.write(f"Image URL: {image_url} (Accessible)\n")
                    else:
                        output_file.write(f"Image URL: {image_url} (Inaccessible)\n")
                output_file.write(f"Video URL: {video_url}\n\n")

def show_progress(current, total):
    progress = (current / total) * 100
    print(f"Прогрес: {progress:.2f}%")

def search_and_index_files(paths):
    file_count = 0
    total_files = sum(len(files) for _, _, files in os.walk(paths[0]))
    with ThreadPoolExecutor() as executor:
        futures = []
        for path in paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".txt"):
                        file_count += 1
                        file_path = os.path.join(root, file)
                        print(f"Знайдено файл: {file_path}")
                        future = executor.submit(process_file, file_path)
                        futures.append(future)

        for future in futures:
            future.result()
            show_progress(file_count, total_files)

    return file_count

search_paths = [
    r"C:\OSPanel\domains\localhostSearchEngine\RobotSE002F\results",
    r"C:\OSPanel\domains\localhostSearchEngine\RobotSE002F\indexed_data",
    r"C:\OSPanel\domains\localhostSearchEngine\RobotSE002F"
]

file_count = search_and_index_files(search_paths)
print(f"Знайдено {file_count} файлів для обробки.")
