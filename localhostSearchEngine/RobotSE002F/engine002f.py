from html.parser import HTMLParser
from urllib.parse import urljoin
import concurrent.futures
import os
import urllib.request
import random
import time

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.title = ""
        self.description = ""
        self.current_tag = None
        self.images = []
        self.videos = []
        self.domain = ""

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    link = attr[1]
                    if link.startswith("javascript:") or "search?q=" in link or link.endswith(("/robots.txt", "/sitemaps.xml")):
                        continue
                    if any(link.startswith(language) for language in IGNORED_LANGUAGES):
                        continue
                    self.links.append(link)
        elif tag == "img":
            image_attrs = dict(attrs)
            image_url = image_attrs.get("src")
            image_alt = image_attrs.get("alt", "")
            image_title = image_attrs.get("title", "")
            if image_url:
                self.images.append({"url": image_url, "alt": image_alt, "title": image_title})
        elif tag == "video":
            video_attrs = dict(attrs)
            video_url = video_attrs.get("src")
            video_title = video_attrs.get("title", "")
            if video_url:
                self.videos.append({"url": video_url, "title": video_title})

        elif tag == "title":
            self.current_tag = "title"
        elif tag == "meta":
            attributes = dict(attrs)
            if "name" in attributes and attributes["name"] == "description":
                if "content" in attributes:
                    self.description = attributes["content"]

    def handle_data(self, data):
        if self.current_tag == "h1" and self.title == "":
            self.title = data.strip()
        elif self.current_tag == "title":
            self.title = data.strip()

    def handle_endtag(self, tag):
        self.current_tag = None


def search(query, search_url, params, filename):
    # Створення файлу, якщо він не існує
    with open(filename, 'w', encoding='utf-8'):
        pass

    url = search_url + '?' + urllib.parse.urlencode(params)

    try:
        # Випадкова затримка перед відправленням запиту
        random_delay()

        with urllib.request.urlopen(url) as response:
            html_content = response.read().decode('utf-8')

            # Створення та використання HTML-парсера
            parser = MyHTMLParser()
            parser.feed(html_content)

            # Доменне ім'я веб-сайту
            parser.domain = urllib.parse.urlparse(url).netloc

            # Перевірка наявності результатів пошуку
            if not parser.links:
                return

            # Перевірка, чи веб-сайт вже проіндексований, перед записом нових даних у файл
            with open(filename, 'r', encoding='utf-8') as file:
                indexed_links = file.readlines()
            indexed_links = [link.strip() for link in indexed_links]

            # Запис нових даних у текстовий файл з кодуванням UTF-8
            with open(filename, 'a', encoding='utf-8') as file:
                file.write("\n\n")
                file.write("Запит: {}\n".format(url))
                file.write("Посилання:\n")
                for link in parser.links:
                    if link.startswith("http") and link not in indexed_links:
                        file.write(link + '\n')

                        # Індексація посилання
                        if link.endswith(('.html', '.htm')):
                            index_page(link)

                file.write("Назва веб-сайту:\n")
                file.write(parser.title + '\n')

                file.write("Опис:\n")
                if not parser.description:
                    file.write("Опис недоступний\n")
                else:
                    file.write(parser.description + '\n')

                file.write("Зображення:\n")
                for image in parser.images:
                    image_url = image["url"]
                    if not image_url.startswith("data:image"):
                        if not image_url.startswith("http"):
                            image_url = urljoin(parser.domain, image_url)
                        file.write("Посилання: {}\n".format(image_url))
                        if image["alt"]:
                            file.write("ALT: {}\n".format(image["alt"]))
                        if image["title"]:
                            file.write("Назва: {}\n".format(image["title"]))

                file.write("Відео:\n")
                for video in parser.videos:
                    video_url = video["url"]
                    if not video_url.startswith("data:video"):
                        if not video_url.startswith("http"):
                            video_url = urljoin(parser.domain, video_url)
                        file.write("Посилання: {}\n".format(video_url))
                        if video["title"]:
                            file.write("Назва: {}\n".format(video["title"]))

                # Запис відео в окремий файл "медіа.тхт"
                with open("media.txt", 'a', encoding='utf-8') as media_file:
                    media_file.write("\n\n")
                    media_file.write("Запит: {}\n".format(url))
                    media_file.write("Відео:\n")
                    for video in parser.videos:
                        video_url = video["url"]
                        if not video_url.startswith("data:video"):
                            if not video_url.startswith("http"):
                                video_url = urljoin(parser.domain, video_url)
                            media_file.write("Посилання: {}\n".format(video_url))
                            if video["title"]:
                                media_file.write("Назва: {}\n".format(video["title"]))

    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"Доступ до {url} заборонено. Пропускаю...")
        else:
            print(f"HTTP-помилка {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"Помилка з'єднання з {url}. Пропускаю...")
        print(f"Причина: {e.reason}")
    except Exception as e:
        print(f"Помилка під час виконання запиту: {str(e)}")



def search_with_timeout(query, search_engines, timeout):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for search_engine in search_engines:
            engine_name = search_engine['name']
            engine_url = search_engine['url']
            engine_params = search_engine.get('params', {})
            results_filename = f"results/{engine_name.lower().replace('.', '_')}_results.txt"

            print(f"Виконується пошук на {engine_name}...")
            futures.append(executor.submit(search, query, engine_url, engine_params, results_filename))

        # Очікування завершення всіх запитів з тайм-аутом для кожного пошукового двигуна
        for future in concurrent.futures.as_completed(futures, timeout=timeout):
            try:
                future.result()
            except Exception as e:
                print(f"Помилка під час виконання запиту: {str(e)}")

        print("Пошук завершено.")

        # Індексування посилань з файлів у папці index_data
        index_data_folder = "index_data"
        if os.path.exists(index_data_folder) and os.path.isdir(index_data_folder):
            indexed_data_filename = "indexed_data/all_indexed_data.txt"
            with open(indexed_data_filename, 'a', encoding='utf-8') as file:
                for filename in os.listdir(index_data_folder):
                    if filename.endswith(".txt"):
                        file_path = os.path.join(index_data_folder, filename)
                        with open(file_path, "r", encoding="utf-8") as f:
                            file.write(f.read())


# Функція для індексації посилання
def index_page(url):
    try:
        with urllib.request.urlopen(url) as response:
            html_content = response.read().decode('utf-8')

            # Створення та використання HTML-парсера
            parser = MyHTMLParser()
            parser.feed(html_content)

            # Перевірка наявності результатів пошуку
            if not parser.links:
                return

            # Створення окремого файлу для проіндексованих даних
            indexed_data_filename = f"indexed_data/{urllib.parse.urlparse(url).netloc.replace('.', '_')}_indexed_data.txt"

            # Збереження проіндексованих даних у текстовий файл з кодуванням UTF-8
            with open(indexed_data_filename, 'a', encoding='utf-8') as file:
                file.write("Посилання: {}\n".format(url))

                file.write("Посилання:\n")
                for link in parser.links:
                    if link.startswith("http"):
                        file.write(link + '\n')

                file.write("Назва веб-сайту:\n")
                file.write(parser.title + '\n')

                file.write("Опис:\n")
                if not parser.description:
                    file.write("Опис недоступний\n")
                else:
                    file.write(parser.description + '\n')

                file.write("Зображення:\n")
                for image in parser.images:
                    image_url = image["url"]
                    if not image_url.startswith("data:image"):
                        if not image_url.startswith("http"):
                            image_url = urljoin(parser.domain, image_url)
                        file.write("Посилання: {}\n".format(image_url))
                        if image["alt"]:
                            file.write("ALT: {}\n".format(image["alt"]))
                        if image["title"]:
                            file.write("Назва: {}\n".format(image["title"]))

                file.write("Відео:\n")
                for video in parser.videos:
                    video_url = video["url"]
                    if not video_url.startswith("data:video"):
                        if not video_url.startswith("http"):
                            video_url = urljoin(parser.domain, video_url)
                        file.write("Посилання: {}\n".format(video_url))
                        if video["title"]:
                            file.write("Назва: {}\n".format(video["title"]))

    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"Доступ до {url} заборонено. Пропускаю...")
        else:
            print(f"HTTP-помилка {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"Помилка з'єднання з {url}. Пропускаю...")
        print(f"Причина: {e.reason}")
    except Exception as e:
        print(f"Помилка під час виконання запиту: {str(e)}")


# Функція для випадкової затримки
def random_delay():
    delay = random.uniform(0.5, 2.0)  # Випадкова затримка між 0.5 та 2.0 секунд
    time.sleep(delay)


# Функція для випадкової зміни регістру літер в запиті
def random_case(query):
    modified_query = ""
    for char in query:
        if random.random() < 0.5:  # 50% ймовірність зміни регістру літери
            modified_query += char.upper() if char.islower() else char.lower()
        else:
            modified_query += char
    return modified_query


# Створення папки для результатів, якщо вона не існує
if not os.path.exists('results'):
    os.makedirs('results')

# Створення папки для проіндексованих даних, якщо вона не існує
if not os.path.exists('indexed_data'):
    os.makedirs('indexed_data')

# Налаштування ігнорування мов
IGNORED_LANGUAGES = [
    "https://fr.pornhub.com/video",
    "https://es.pornhub.com/video",
    "https://it.pornhub.com/video",
    "https://pt.pornhub.com/video",
    "https://pl.pornhub.com/video",
    "https://rt.pornhub.com/video",
    "https://jp.pornhub.com/video",
    "https://nl.pornhub.com/video",
    "https://cz.pornhub.com/video",
    "https://cn.pornhub.com/video"
]

# Функція для обробки результатів з pornhub_results.txt
def process_pornhub_results():
    pornhub_results_filename = "results/pornhub_results.txt"
    indexed_data_folder = "indexed_data"

    if not os.path.exists(indexed_data_folder):
        os.makedirs(indexed_data_folder)

    # Перевірка наявності файлу pornhub_results.txt
    if os.path.exists(pornhub_results_filename):
        with open(pornhub_results_filename, 'r', encoding='utf-8') as file:
            links = file.readlines()

        # Видалення пробільних символів з кожного посилання та видалення дублікатів
        links = [link.strip() for link in links]
        links = list(set(links))

        # Обробка кожного посилання та збереження проіндексованих даних у текстовий файл
        for link in links:
            if link.startswith("http"):
                indexed_data_filename = f"{indexed_data_folder}/{urllib.parse.urlparse(link).netloc.replace('.', '_')}_indexed_data.txt"
                index_page(link)
                print(f"Проіндексовано: {link}")
                print(f"Проіндексовані дані збережено у файлі: {indexed_data_filename}")
                print("-" * 50)

# Приклад пошукового запиту

queries = [
'Cat',
'Природа',
'Собака',
'Кот',
]


timeout = 30  # Максимальний таймаут для кожного пошукового двигуна

# Пошукові двигуни
search_engines = [
    {'name': 'Mail.ru', 'url': 'https://www.mail.ru/search', 'params': {'num': 50}},
    {'name': 'Bing', 'url': 'https://www.bing.com/search', 'params': {'count': 50}},
    {'name': 'DuckDuckGo', 'url': 'https://duckduckgo.com/html', 'params': {'kl': 'us-en'}},
    {'name': 'Yandex', 'url': 'https://yandex.com/search', 'params': {'numdoc': 50}},
    {'name': 'Google', 'url': 'https://www.google.com/search', 'params': {'num': 50}},
    {'name': 'AOL', 'url': 'https://search.aol.com/aol/search', 'params': {'count': 50}},
    {'name': 'Ask', 'url': 'https://www.ask.com/web', 'params': {'qsrc': '0', 'count': 50}},
    {'name': 'Wow', 'url': 'https://www.wow.com/search', 'params': {'count': 50}},
    {'name': 'WebCrawler', 'url': 'https://www.webcrawler.com/serp', 'params': {'ispeed': '1', 'p': 50}},
    {'name': 'jut-su.net', 'url': 'https://jut-su.net/search'} 
]

# Додаткові сайти для пошуку 
additional_sites = [

    # {'name': 'YouTube', 'url': 'https://www.youtube.com/results', 'params': {'search_query': ''}},
    # {'name': 'PornHub', 'url': 'https://www.pornhub.com/video/search', 'params': {'search': ''}},
    # {'name': 'Netflix', 'url': 'https://www.netflix.com/search', 'params': {'q': ''}},
    # {'name': 'Wikipedia', 'url': 'https://en.wikipedia.org/wiki/Special:Search', 'params': {'search': ''}},
    # {'name': 'Unreal Engine', 'url': 'https://www.unrealengine.com/search', 'params': {'q': ''}},
    # {'name': 'Unity', 'url': 'https://unity.com/search', 'params': {'q': ''}},
    # {'name': 'Kissanime', 'url': 'https://kissanime.ru/search.html', 'params': {'keyword': ''}},
    # {'name': 'Dramacool', 'url': 'https://www.dramacool.info/search.html', 'params': {'keyword': ''}},
    # {'name': 'Useful Site', 'url': 'https://www.usefulsite.com/search', 'params': {'q': ''}},

    # {'name': 'Vimeo', 'url': 'https://vimeo.com/search', 'params': {'q': ''}},
    # {'name': 'Dailymotion', 'url': 'https://www.dailymotion.com/search', 'params': {'query': ''}},
    # {'name': 'Twitch', 'url': 'https://www.twitch.tv/search', 'params': {'query': ''}},
    # {'name': 'Veoh', 'url': 'https://www.veoh.com/find/', 'params': {'searchText': ''}},
    # {'name': 'Metacafe', 'url': 'https://www.metacafe.com/videos_about/', 'params': {'search': ''}},

    # {'name': 'Vimeo', 'url': 'https://vimeo.com/search', 'params': {'q': ''}},
    # {'name': 'IMDb', 'url': 'https://www.imdb.com/find', 'params': {'q': '', 's': 'all'}},
    # {'name': 'Stack Overflow', 'url': 'https://stackoverflow.com/search', 'params': {'q': ''}},
    # {'name': 'GitHub', 'url': 'https://github.com/search', 'params': {'q': ''}},
    # {'name': 'Medium', 'url': 'https://medium.com/search', 'params': {'q': ''}},

    # {'name': 'Google Images', 'url': 'https://www.google.com/search', 'params': {'tbm': 'isch', 'q': ''}},
    # {'name': 'Yahoo', 'url': 'https://search.yahoo.com/search', 'params': {'p': ''}},
    # {'name': 'Bing Images', 'url': 'https://www.bing.com/images/search', 'params': {'q': ''}},
    # {'name': 'Twitter', 'url': 'https://twitter.com/search', 'params': {'q': ''}},
    # {'name': 'Facebook', 'url': 'https://www.facebook.com/search', 'params': {'q': ''}},
    # {'name': 'Instagram', 'url': 'https://www.instagram.com/explore/tags', 'params': {'tag': ''}},
    # {'name': 'Pinterest', 'url': 'https://www.pinterest.com/search', 'params': {'q': ''}},
    # {'name': 'Reddit', 'url': 'https://www.reddit.com/search', 'params': {'q': ''}},
    # {'name': 'Quora', 'url': 'https://www.quora.com/search', 'params': {'q': ''}},
    # {'name': 'Tumblr', 'url': 'https://www.tumblr.com/search', 'params': {'q': ''}},
    # {'name': 'Flickr', 'url': 'https://www.flickr.com/search', 'params': {'text': ''}},
    # {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/search/results', 'params': {'keywords': ''}},
    # {'name': 'Wordpress', 'url': 'https://wordpress.com/search', 'params': {'query': ''}},
    # {'name': 'Ebay', 'url': 'https://www.ebay.com/sch', 'params': {'_nkw': ''}},
    # {'name': 'AliExpress', 'url': 'https://www.aliexpress.com/wholesale', 'params': {'SearchText': ''}},
    # {'name': 'CNN', 'url': 'https://www.cnn.com/search', 'params': {'q': ''}},
    # {'name': 'BBC', 'url': 'https://www.bbc.co.uk/search', 'params': {'q': ''}},
    # {'name': 'The New York Times', 'url': 'https://www.nytimes.com/search', 'params': {'query': ''}},
    # {'name': 'Reuters', 'url': 'https://www.reuters.com/search/news', 'params': {'blob': ''}},
    # {'name': 'The Guardian', 'url': 'https://www.theguardian.com/search', 'params': {'q': ''}},
    # {'name': 'National Geographic', 'url': 'https://www.nationalgeographic.com/search', 'params': {'q': ''}},
    # {'name': 'TED', 'url': 'https://www.ted.com/search', 'params': {'q': ''}},
    # {'name': 'Academic Search', 'url': 'https://www.semanticscholar.org/search', 'params': {'q': ''}},
    # {'name': 'ScienceDirect', 'url': 'https://www.sciencedirect.com/search', 'params': {'query': ''}},
    # {'name': 'IEEE Xplore', 'url': 'https://ieeexplore.ieee.org/search/searchresult.jsp', 'params': {'queryText': ''}},
    # {'name': 'ArXiv', 'url': 'https://arxiv.org/search', 'params': {'query': '', 'searchtype': 'all'}},
    # {'name': 'ResearchGate', 'url': 'https://www.researchgate.net/search.Search.html', 'params': {'query': ''}},
    # {'name': 'Coursera', 'url': 'https://www.coursera.org/search', 'params': {'query': ''}},
    # {'name': 'Udemy', 'url': 'https://www.udemy.com/courses/search', 'params': {'q': ''}},
    # {'name': 'Khan Academy', 'url': 'https://www.khanacademy.org/search', 'params': {'q': ''}},
    # {'name': 'Goodreads', 'url': 'https://www.goodreads.com/search', 'params': {'q': ''}},
    # {'name': 'Last.fm', 'url': 'https://www.last.fm/search', 'params': {'q': ''}},
    # {'name': 'AllMusic', 'url': 'https://www.allmusic.com/search', 'params': {'search': ''}},
    

    #     {'name': 'Spotify', 'url': 'https://www.spotify.com/search/results', 'params': {'q': ''}},
    # {'name': 'Apple Music', 'url': 'https://music.apple.com/search', 'params': {'term': ''}},
    # {'name': 'TikTok', 'url': 'https://www.tiktok.com/search', 'params': {'q': ''}},
    # {'name': 'Vine', 'url': 'https://vine.co/search', 'params': {'query': ''}},
    # {'name': 'Snapchat', 'url': 'https://www.snapchat.com/search', 'params': {'q': ''}},
    # {'name': 'WhatsApp', 'url': 'https://api.whatsapp.com/send', 'params': {'text': ''}},
    # {'name': 'Skype', 'url': 'https://secure.skype.com/portal/search', 'params': {'q': ''}},
    # {'name': 'Slack', 'url': 'https://slack.com/intl/en-gb/help/articles/204999038', 'params': {'q': ''}},
    # {'name': 'Pinterest', 'url': 'https://www.pinterest.com/search', 'params': {'q': ''}},
    # {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/search/results', 'params': {'keywords': ''}},
    # {'name': 'Etsy', 'url': 'https://www.etsy.com/search', 'params': {'q': ''}},
    # {'name': 'Booking.com', 'url': 'https://www.booking.com/searchresults', 'params': {'ss': ''}},
    # {'name': 'Airbnb', 'url': 'https://www.airbnb.com/s', 'params': {'location': ''}},
    # {'name': 'TripAdvisor', 'url': 'https://www.tripadvisor.com/Search', 'params': {'q': ''}},
    # {'name': 'Zillow', 'url': 'https://www.zillow.com/homes/for_sale', 'params': {'searchQueryState': ''}},
    # {'name': 'Realtor.com', 'url': 'https://www.realtor.com/realestateandhomes-search', 'params': {'search': ''}},
    # {'name': 'AutoTrader', 'url': 'https://www.autotrader.com/cars-for-sale/searchresults.xhtml', 'params': {'searchRadius': '', 'location': ''}},
    # {'name': 'Indeed', 'url': 'https://www.indeed.com/jobs', 'params': {'q': ''}},
    # {'name': 'Glassdoor', 'url': 'https://www.glassdoor.com/Job/jobs.htm', 'params': {'keyword': ''}},
    # {'name': 'Monster', 'url': 'https://www.monster.com/jobs/search', 'params': {'q': ''}},
    # {'name': 'Upwork', 'url': 'https://www.upwork.com/search/jobs', 'params': {'q': ''}},
    # {'name': 'Freelancer', 'url': 'https://www.freelancer.com/work', 'params': {'keyword': ''}},
    # {'name': 'Fiverr', 'url': 'https://www.fiverr.com/search/gigs', 'params': {'query': ''}},
    # {'name': 'Craigslist', 'url': 'https://www.craigslist.org/search', 'params': {'query': ''}},
    # {'name': 'Groupon', 'url': 'https://www.groupon.com/browse', 'params': {'query': ''}},
    # {'name': 'Yelp', 'url': 'https://www.yelp.com/search', 'params': {'find_desc': ''}},
    # {'name': 'IMDb', 'url': 'https://www.imdb.com/find', 'params': {'q': '', 's': 'all'}},
    # {'name': 'Rotten Tomatoes', 'url': 'https://www.rottentomatoes.com/search', 'params': {'search': ''}},
    # {'name': 'Metacritic', 'url': 'https://www.metacritic.com/search/all', 'params': {'search_type': 'movies', 'search': ''}},
    # {'name': 'Goodreads', 'url': 'https://www.goodreads.com/search', 'params': {'q': ''}},
    # {'name': 'Food Network', 'url': 'https://www.foodnetwork.com/search', 'params': {'q': ''}},
    # {'name': 'AllRecipes', 'url': 'https://www.allrecipes.com/search/results', 'params': {'search': ''}},
    # {'name': 'Epicurious', 'url': 'https://www.epicurious.com/search', 'params': {'search': ''}},
    # {'name': 'OpenTable', 'url': 'https://www.opentable.com/s', 'params': {'keywords': ''}},
    # {'name': 'Zomato', 'url': 'https://www.zomato.com/search', 'params': {'q': ''}},
    # {'name': 'Uber Eats', 'url': 'https://www.ubereats.com/search', 'params': {'q': ''}},
    # {'name': 'DoorDash', 'url': 'https://www.doordash.com/search', 'params': {'q': ''}},
    # {'name': 'Postmates', 'url': 'https://postmates.com/search', 'params': {'q': ''}},
    # {'name': 'Instacart', 'url': 'https://www.instacart.com/store/search_v3', 'params': {'s': '', 'q': ''}},
    # {'name': 'Grubhub', 'url': 'https://www.grubhub.com/search', 'params': {'searchTerm': ''}},
    # {'name': 'Caviar', 'url': 'https://www.trycaviar.com/search', 'params': {'searchTerm': ''}},
    # {'name': 'Deliveroo', 'url': 'https://deliveroo.co.uk/restaurants', 'params': {'q': ''}},
    # {'name': 'Swiggy', 'url': 'https://www.swiggy.com/search', 'params': {'q': ''}},
    # {'name': 'Just Eat', 'url': 'https://www.just-eat.co.uk/search', 'params': {'q': ''}},
    # {'name': 'Doorstep Delivery', 'url': 'https://www.doorstepdelivery.com/search', 'params': {'q': ''}},
    # {'name': 'Walmart', 'url': 'https://www.walmart.com/search', 'params': {'query': ''}},
    # {'name': 'eBay', 'url': 'https://www.ebay.com/sch', 'params': {'_nkw': ''}},
    # {'name': 'Best Buy', 'url': 'https://www.bestbuy.com/site/searchpage', 'params': {'query': ''}},
    # {'name': 'Target', 'url': 'https://www.target.com/s', 'params': {'searchTerm': ''}},
    # {'name': 'Home Depot', 'url': 'https://www.homedepot.com/s', 'params': {'keyword': ''}},
    # {'name': 'Lowe\'s', 'url': 'https://www.lowes.com/search', 'params': {'q': ''}},
    # {'name': 'Staples', 'url': 'https://www.staples.com/s', 'params': {'q': ''}},
    # {'name': 'Office Depot', 'url': 'https://www.officedepot.com/catalog/search', 'params': {'query': ''}},
    # {'name': 'CVS', 'url': 'https://www.cvs.com/search', 'params': {'searchTerm': ''}},

    #     {'name': 'Український YouTube', 'url': 'https://www.youtube.com/results', 'params': {'search_query': ''}},
    # {'name': 'Український Google', 'url': 'https://www.google.com/search', 'params': {'q': ''}},
    # {'name': 'Українська Wikipedia', 'url': 'https://uk.wikipedia.org/wiki/Спеціальна:Пошук', 'params': {'search': ''}},
    # {'name': 'Український OLX', 'url': 'https://www.olx.ua/uk/', 'params': {'q': ''}},
    # {'name': 'Український Prom.ua', 'url': 'https://prom.ua/ua/search', 'params': {'search_term': ''}},
    # {'name': 'Український Rozetka', 'url': 'https://rozetka.com.ua/ua/search/', 'params': {'text': ''}},
    # {'name': 'Український Zakaz.ua', 'url': 'https://zakaz.ua/ukr/uk/search', 'params': {'query': ''}},
    # {'name': 'Український Price.ua', 'url': 'https://price.ua/search', 'params': {'q': ''}},
    # {'name': 'Український Yandex', 'url': 'https://yandex.ua/search/', 'params': {'text': ''}},
    # {'name': 'Український Meta.ua', 'url': 'https://www.meta.ua/ua/search/', 'params': {'q': ''}},
    # {'name': 'Український Корреспондент', 'url': 'https://ua.korrespondent.net/', 'params': {}},
    # {'name': 'Український УНІАН', 'url': 'https://www.unian.ua/', 'params': {}},
    # {'name': 'Український Інтерфакс-Україна', 'url': 'https://www.interfax.com.ua/', 'params': {}},
    # {'name': 'Український Європейська правда', 'url': 'https://www.eurointegration.com.ua/', 'params': {}},
    # {'name': 'Український Українська правда', 'url': 'https://www.pravda.com.ua/', 'params': {}},
    # {'name': 'Український Цензор.НЕТ', 'url': 'https://censor.net.ua/', 'params': {}},
    # {'name': 'Український ТСН', 'url': 'https://tsn.ua/', 'params': {}},
    # {'name': 'Український Сегодня', 'url': 'https://www.segodnya.ua/', 'params': {}},
    # {'name': 'Український УП', 'url': 'https://www.pravda.com.ua/', 'params': {}},
    # {'name': 'Український Українські новини', 'url': 'https://www.ukrinform.ua/', 'params': {}},
    # {'name': 'Український Українська правда', 'url': 'https://www.pravda.com.ua/', 'params': {}},
    # {'name': 'Український Український Тиждень', 'url': 'https://tyzhden.ua/', 'params': {}},
    # {'name': 'Український ЛІГА', 'url': 'https://www.liga.net/', 'params': {}},
    # {'name': 'Український Главком', 'url': 'https://glavcom.ua/', 'params': {}},
    # {'name': 'Український 24 Канал', 'url': 'https://24tv.ua/', 'params': {}},
    # {'name': 'Український Новое Время', 'url': 'https://nv.ua/', 'params': {}},
    # {'name': 'Український Оглядовий портал', 'url': 'https://www.obozrevatel.com/', 'params': {}},
    # {'name': 'Український Громадське', 'url': 'https://hromadske.ua/', 'params': {}},
    # {'name': 'Український УНІАН', 'url': 'https://www.unian.ua/', 'params': {}},
    # {'name': 'Український Інтерфакс-Україна', 'url': 'https://www.interfax.com.ua/', 'params': {}},
    # {'name': 'Український Українська правда', 'url': 'https://www.pravda.com.ua/', 'params': {}},
    # {'name': 'Український Європейська правда', 'url': 'https://www.eurointegration.com.ua/', 'params': {}},
    # {'name': 'Український Українська правда', 'url': 'https://www.pravda.com.ua/', 'params': {}},
    # {'name': 'Український Цензор.НЕТ', 'url': 'https://censor.net.ua/', 'params': {}},
    # {'name': 'Український ТСН', 'url': 'https://tsn.ua/', 'params': {}},
    # {'name': 'Український Сегодня', 'url': 'https://www.segodnya.ua/', 'params': {}},
    # {'name': 'Український УП', 'url': 'https://www.pravda.com.ua/', 'params': {}},
    # {'name': 'Український Українські новини', 'url': 'https://www.ukrinform.ua/', 'params': {}},
    # {'name': 'Український Українська правда', 'url': 'https://www.pravda.com.ua/', 'params': {}},
    # {'name': 'Український Український Тиждень', 'url': 'https://tyzhden.ua/', 'params': {}},
    # {'name': 'Український ЛІГА', 'url': 'https://www.liga.net/', 'params': {}},
    # {'name': 'Український Главком', 'url': 'https://glavcom.ua/', 'params': {}},
    # {'name': 'Український 24 Канал', 'url': 'https://24tv.ua/', 'params': {}},
    # {'name': 'Український Новое Время', 'url': 'https://nv.ua/', 'params': {}},
    # {'name': 'Український Оглядовий портал', 'url': 'https://www.obozrevatel.com/', 'params': {}},
    # {'name': 'Український Громадське', 'url': 'https://hromadske.ua/', 'params': {}},

    #     {'name': 'Російський YouTube', 'url': 'https://www.youtube.com/results', 'params': {'search_query': ''}},
    # {'name': 'Російський Google', 'url': 'https://www.google.com/search', 'params': {'q': ''}},
    # {'name': 'Російська Wikipedia', 'url': 'https://ru.wikipedia.org/wiki/Специальная:Поиск', 'params': {'search': ''}},
    # {'name': 'Російський Yandex', 'url': 'https://yandex.ru/search/', 'params': {'text': ''}},
    # {'name': 'Російський Mail.ru', 'url': 'https://go.mail.ru/search', 'params': {'q': ''}},
    # {'name': 'Російський Rambler', 'url': 'https://www.rambler.ru/search', 'params': {'query': ''}},
    # {'name': 'Російський Яндекс.Маркет', 'url': 'https://market.yandex.ru/search', 'params': {'text': ''}},
    # {'name': 'Російський Avito', 'url': 'https://www.avito.ru/', 'params': {'q': ''}},
    # {'name': 'Російський Ozon', 'url': 'https://www.ozon.ru/search/', 'params': {'text': ''}},
    # {'name': 'Російський Wildberries', 'url': 'https://www.wildberries.ru/catalog/0/search.aspx', 'params': {'search': ''}},
    # {'name': 'Російський Lamoda', 'url': 'https://www.lamoda.ru/catalogsearch/result/', 'params': {'q': ''}},
    # {'name': 'Російський Citilink', 'url': 'https://www.citilink.ru/search/', 'params': {'text': ''}},
    # {'name': 'Російський DNS Shop', 'url': 'https://www.dns-shop.ru/search/', 'params': {'q': ''}},
    # {'name': 'Російський 1C-Interes', 'url': 'https://www.1c-interes.ru/catalog/search/', 'params': {'q': ''}},
    # {'name': 'Російський Tinkoff', 'url': 'https://www.tinkoff.ru/search/', 'params': {'query': ''}},
    # {'name': 'Російський TJournal', 'url': 'https://tjournal.ru/', 'params': {}},
    # {'name': 'Російський РИА Новости', 'url': 'https://ria.ru/', 'params': {}},
    # {'name': 'Російський Lenta.ru', 'url': 'https://lenta.ru/', 'params': {}},
    # {'name': 'Російський RT', 'url': 'https://russian.rt.com/', 'params': {}},
    # {'name': 'Російський Известия', 'url': 'https://iz.ru/', 'params': {}},
    # {'name': 'Російський RBC', 'url': 'https://www.rbc.ru/', 'params': {}},
    # {'name': 'Російський Вести.Ru', 'url': 'https://www.vesti.ru/', 'params': {}},
    # {'name': 'Російський Gazeta.ru', 'url': 'https://www.gazeta.ru/', 'params': {}},
    # {'name': 'Російський Коммерсантъ', 'url': 'https://www.kommersant.ru/', 'params': {}},
    # {'name': 'Російський Новая Газета', 'url': 'https://novayagazeta.ru/', 'params': {}},
    # {'name': 'Російський Московський Комсомолець', 'url': 'https://www.mk.ru/', 'params': {}},
    # {'name': 'Російський Life', 'url': 'https://life.ru/', 'params': {}},
    # {'name': 'Російський Комсомольська правда', 'url': 'https://www.kp.ru/', 'params': {}},
    # {'name': 'Російський Российская газета', 'url': 'https://rg.ru/', 'params': {}},
    # {'name': 'Російський Звезда', 'url': 'https://tvzvezda.ru/', 'params': {}},
    # {'name': 'Російський Спорт-Експрес', 'url': 'https://www.sport-express.ru/', 'params': {}},
    # {'name': 'Російський Чемпионат', 'url': 'https://www.championat.com/', 'params': {}},
    # {'name': 'Російський Sports.ru', 'url': 'https://www.sports.ru/', 'params': {}},
    # {'name': 'Російський Фонтанка.ру', 'url': 'https://www.fontanka.ru/', 'params': {}},
    # {'name': 'Російський KP.RU', 'url': 'https://www.kp.ru/', 'params': {}},
    # {'name': 'Російський RIA', 'url': 'https://www.ria.ru/', 'params': {}},
    # {'name': 'Російський Лента.ру', 'url': 'https://lenta.ru/', 'params': {}},
    # {'name': 'Російський RT на русском', 'url': 'https://russian.rt.com/', 'params': {}},
    # {'name': 'Російський Известия', 'url': 'https://iz.ru/', 'params': {}},
    # {'name': 'Російський РБК', 'url': 'https://www.rbc.ru/', 'params': {}},
    # {'name': 'Російський Вести.Ru', 'url': 'https://www.vesti.ru/', 'params': {}},
    # {'name': 'Російський Газета.Ru', 'url': 'https://www.gazeta.ru/', 'params': {}},
    # {'name': 'Російський Коммерсантъ', 'url': 'https://www.kommersant.ru/', 'params': {}},
    # {'name': 'Російський Новая Газета', 'url': 'https://novayagazeta.ru/', 'params': {}},
    # {'name': 'Російський Московский Комсомолец', 'url': 'https://www.mk.ru/', 'params': {}},
    # {'name': 'Російський Life', 'url': 'https://life.ru/', 'params': {}},
    # {'name': 'Російський Комсомольская правда', 'url': 'https://www.kp.ru/', 'params': {}},
    # {'name': 'Російський Российская газета', 'url': 'https://rg.ru/', 'params': {}},
    # {'name': 'Російський Звезда', 'url': 'https://tvzvezda.ru/', 'params': {}},
    # {'name': 'Російський Спорт-Экспресс', 'url': 'https://www.sport-express.ru/', 'params': {}},
    # {'name': 'Російський Чемпионат', 'url': 'https://www.championat.com/', 'params': {}},
    # {'name': 'Російський Sports.ru', 'url': 'https://www.sports.ru/', 'params': {}},



    #     # США
    # {'name': 'CNN', 'url': 'https://www.cnn.com/', 'params': {}},
    # {'name': 'The New York Times', 'url': 'https://www.nytimes.com/', 'params': {}},
    # {'name': 'HuffPost', 'url': 'https://www.huffpost.com/', 'params': {}},
    # {'name': 'ESPN', 'url': 'https://www.espn.com/', 'params': {}},
    # {'name': 'Wikipedia', 'url': 'https://en.wikipedia.org/', 'params': {}},

    # # Великобританія
    # {'name': 'BBC', 'url': 'https://www.bbc.co.uk/', 'params': {}},
    # {'name': 'The Guardian', 'url': 'https://www.theguardian.com/', 'params': {}},
    # {'name': 'Daily Mail', 'url': 'https://www.dailymail.co.uk/', 'params': {}},
    # {'name': 'The Times', 'url': 'https://www.thetimes.co.uk/', 'params': {}},
    # {'name': 'Sky News', 'url': 'https://news.sky.com/', 'params': {}},

    # # Канада
    # {'name': 'CBC', 'url': 'https://www.cbc.ca/', 'params': {}},
    # {'name': 'CTV News', 'url': 'https://www.ctvnews.ca/', 'params': {}},
    # {'name': 'Global News', 'url': 'https://globalnews.ca/', 'params': {}},
    # {'name': 'The Globe and Mail', 'url': 'https://www.theglobeandmail.com/', 'params': {}},
    # {'name': 'National Post', 'url': 'https://nationalpost.com/', 'params': {}},

    # # Австралія
    # {'name': 'ABC News', 'url': 'https://www.abc.net.au/news/', 'params': {}},
    # {'name': 'The Sydney Morning Herald', 'url': 'https://www.smh.com.au/', 'params': {}},
    # {'name': 'News.com.au', 'url': 'https://www.news.com.au/', 'params': {}},
    # {'name': '9News', 'url': 'https://www.9news.com.au/', 'params': {}},
    # {'name': 'The Age', 'url': 'https://www.theage.com.au/', 'params': {}},

    # # Франція
    # {'name': 'Le Monde', 'url': 'https://www.lemonde.fr/', 'params': {}},
    # {'name': 'Le Figaro', 'url': 'https://www.lefigaro.fr/', 'params': {}},
    # {'name': 'Libération', 'url': 'https://www.liberation.fr/', 'params': {}},
    # {'name': 'France 24', 'url': 'https://www.france24.com/', 'params': {}},
    # {'name': 'BFMTV', 'url': 'https://www.bfmtv.com/', 'params': {}},

    # # Німеччина
    # {'name': 'Bild', 'url': 'https://www.bild.de/', 'params': {}},
    # {'name': 'Der Spiegel', 'url': 'https://www.spiegel.de/', 'params': {}},
    # {'name': 'Frankfurter Allgemeine Zeitung', 'url': 'https://www.faz.net/', 'params': {}},
    # {'name': 'Die Welt', 'url': 'https://www.welt.de/', 'params': {}},
    # {'name': 'Süddeutsche Zeitung', 'url': 'https://www.sueddeutsche.de/', 'params': {}},

    # # Іспанія
    # {'name': 'El País', 'url': 'https://elpais.com/', 'params': {}},
    # {'name': 'ABC', 'url': 'https://www.abc.es/', 'params': {}},
    # {'name': 'El Mundo', 'url': 'https://www.elmundo.es/', 'params': {}},
    # {'name': 'La Vanguardia', 'url': 'https://www.lavanguardia.com/', 'params': {}},
    # {'name': 'Marca', 'url': 'https://www.marca.com/', 'params': {}},

    # # Італія
    # {'name': 'La Repubblica', 'url': 'https://www.repubblica.it/', 'params': {}},
    # {'name': 'Corriere della Sera', 'url': 'https://www.corriere.it/', 'params': {}},
    # {'name': 'La Stampa', 'url': 'https://www.lastampa.it/', 'params': {}},
    # {'name': 'Il Sole 24 Ore', 'url': 'https://www.ilsole24ore.com/', 'params': {}},
    # {'name': 'Il Messaggero', 'url': 'https://www.ilmessaggero.it/', 'params': {}},

    # # Індія
    # {'name': 'Times of India', 'url': 'https://timesofindia.indiatimes.com/', 'params': {}},
    # {'name': 'Hindustan Times', 'url': 'https://www.hindustantimes.com/', 'params': {}},
    # {'name': 'Indian Express', 'url': 'https://indianexpress.com/', 'params': {}},
    # {'name': 'The Hindu', 'url': 'https://www.thehindu.com/', 'params': {}},
    # {'name': 'NDTV', 'url': 'https://www.ndtv.com/', 'params': {}},

    # # Бразилія
    # {'name': 'Globo', 'url': 'https://www.globo.com/', 'params': {}},
    # {'name': 'UOL', 'url': 'https://www.uol.com.br/', 'params': {}},
    # {'name': 'Folha de S.Paulo', 'url': 'https://www.folha.uol.com.br/', 'params': {}},
    # {'name': 'Estadão', 'url': 'https://www.estadao.com.br/', 'params': {}},
    # {'name': 'R7', 'url': 'https://www.r7.com/', 'params': {}},

    # # Китай
    # {'name': 'Xinhua', 'url': 'http://www.xinhuanet.com/', 'params': {}},
    # {'name': 'CCTV', 'url': 'http://www.cctv.com/', 'params': {}},
    # {'name': 'People\'s Daily', 'url': 'http://en.people.cn/', 'params': {}},
    # {'name': 'China Daily', 'url': 'http://www.chinadaily.com.cn/', 'params': {}},
    # {'name': 'Global Times', 'url': 'http://www.globaltimes.cn/', 'params': {}},

    # # Південна Корея
    # {'name': 'Yonhap News Agency', 'url': 'https://en.yna.co.kr/', 'params': {}},
    # {'name': 'The Korea Times', 'url': 'https://www.koreatimes.co.kr/', 'params': {}},
    # {'name': 'JoongAng Ilbo', 'url': 'https://www.joongang.co.kr/', 'params': {}},
    # {'name': 'Chosun Ilbo', 'url': 'https://www.chosun.com/', 'params': {}},
    # {'name': 'Hankyoreh', 'url': 'https://www.hani.co.kr/', 'params': {}},

    # # Іран
    # {'name': 'Tasnim News Agency', 'url': 'https://www.tasnimnews.com/', 'params': {}},
    # {'name': 'PressTV', 'url': 'https://www.presstv.ir/', 'params': {}},
    # {'name': 'Mehr News Agency', 'url': 'https://en.mehrnews.com/', 'params': {}},
    # {'name': 'Iran Daily', 'url': 'https://iran-daily.com/', 'params': {}},
    # {'name': 'Fars News Agency', 'url': 'https://en.farsnews.ir/', 'params': {}},

    # # Індонезія
    # {'name': 'Kompas', 'url': 'https://www.kompas.com/', 'params': {}},
    # {'name': 'Detik', 'url': 'https://www.detik.com/', 'params': {}},
    # {'name': 'Tribunnews', 'url': 'https://www.tribunnews.com/', 'params': {}},
    # {'name': 'CNN Indonesia', 'url': 'https://www.cnnindonesia.com/', 'params': {}},
    # {'name': 'Tempo', 'url': 'https://www.tempo.co/', 'params': {}},

    # # Мексика
    # {'name': 'El Universal', 'url': 'https://www.eluniversal.com.mx/', 'params': {}},
    # {'name': 'Excélsior', 'url': 'https://www.excelsior.com.mx/', 'params': {}},
    # {'name': 'Milenio', 'url': 'https://www.milenio.com/', 'params': {}},
    # {'name': 'Reforma', 'url': 'https://www.reforma.com/', 'params': {}},
    # {'name': 'Televisa News', 'url': 'https://noticieros.televisa.com/', 'params': {}},

    # # Швеція
    # {'name': 'SVT', 'url': 'https://www.svt.se/', 'params': {}},
    # {'name': 'Aftonbladet', 'url': 'https://www.aftonbladet.se/', 'params': {}},
    # {'name': 'Expressen', 'url': 'https://www.expressen.se/', 'params': {}},
    # {'name': 'Dagens Nyheter', 'url': 'https://www.dn.se/', 'params': {}},
    # {'name': 'Svenska Dagbladet', 'url': 'https://www.svd.se/', 'params': {}},

    # # Нідерланди
    # {'name': 'NOS', 'url': 'https://nos.nl/', 'params': {}},
    # {'name': 'De Telegraaf', 'url': 'https://www.telegraaf.nl/', 'params': {}},
    # {'name': 'AD', 'url': 'https://www.ad.nl/', 'params': {}},
    # {'name': 'NRC', 'url': 'https://www.nrc.nl/', 'params': {}},
    # {'name': 'Volkskrant', 'url': 'https://www.volkskrant.nl/', 'params': {}},

    # #Japanese
    # {'name': 'Yahoo! Japan', 'url': 'https://www.yahoo.co.jp/', 'params': {}},
    # {'name': 'Google Japan', 'url': 'https://www.google.co.jp/', 'params': {}},
    # {'name': 'NHK', 'url': 'https://www3.nhk.or.jp/news/', 'params': {}},
    # {'name': 'Asahi Shimbun', 'url': 'https://www.asahi.com/', 'params': {}},
    # {'name': 'Yomiuri Shimbun', 'url': 'https://www.yomiuri.co.jp/', 'params': {}},
    # {'name': 'Mainichi Shimbun', 'url': 'https://mainichi.jp/', 'params': {}},
    # {'name': 'Nikkei', 'url': 'https://www.nikkei.com/', 'params': {}},
    # {'name': 'Sankei News', 'url': 'https://www.sankei.com/', 'params': {}},
    # {'name': 'Kyodo News', 'url': 'https://english.kyodonews.net/', 'params': {}},
    # {'name': 'Japan Times', 'url': 'https://www.japantimes.co.jp/', 'params': {}},
    # {'name': 'Sponichi Annex', 'url': 'https://www.sponichi.co.jp/', 'params': {}},
    # {'name': 'Sports Nippon', 'url': 'https://www.sponichi.co.jp/', 'params': {}},
    # {'name': 'Nikkansports.com', 'url': 'https://www.nikkansports.com/', 'params': {}},
    # {'name': 'Tokyo Shimbun', 'url': 'https://www.tokyo-np.co.jp/', 'params': {}},
    # {'name': 'Chunichi Sports', 'url': 'https://www.chunichi.co.jp/', 'params': {}},
    # {'name': 'Nikkō Keizai Shimbun', 'url': 'https://www.nikkei.com/', 'params': {}},
    # {'name': 'Kahoku Shimpo', 'url': 'https://www.kahoku.co.jp/', 'params': {}},
    # {'name': 'Rakuten', 'url': 'https://www.rakuten.co.jp/', 'params': {}},
    # {'name': 'Amazon Japan', 'url': 'https://www.amazon.co.jp/', 'params': {}},
    # {'name': 'Rakuten Ichiba', 'url': 'https://www.rakuten.co.jp/', 'params': {}},
    # {'name': 'Amazon.co.jp', 'url': 'https://www.amazon.co.jp/', 'params': {}},
    # {'name': 'Wowma!', 'url': 'https://wowma.jp/', 'params': {}},
    # {'name': 'PayPay Mall', 'url': 'https://paypaymall.yahoo.co.jp/', 'params': {}},
    # {'name': 'DMM.com', 'url': 'https://www.dmm.com/', 'params': {}},
    # {'name': 'Goo', 'url': 'https://www.goo.ne.jp/', 'params': {}},
    # {'name': 'Kakaku.com', 'url': 'https://kakaku.com/', 'params': {}},
    # {'name': 'BIGLOBE', 'url': 'https://www.biglobe.ne.jp/', 'params': {}},
    # {'name': 'FC2', 'url': 'https://fc2.com/', 'params': {}},
    # {'name': 'Infoseek', 'url': 'https://www.infoseek.co.jp/', 'params': {}},
    # {'name': '5ch.net', 'url': 'https://5ch.net/', 'params': {}},
    # {'name': 'Nifty', 'url': 'https://www.nifty.com/', 'params': {}},
    # {'name': 'Gunosy', 'url': 'https://gunosy.com/', 'params': {}},
    # {'name': 'livedoor', 'url': 'https://www.livedoor.com/', 'params': {}},
    # {'name': 'Zozo', 'url': 'https://zozo.jp/', 'params': {}},
    # {'name': 'Mercari', 'url': 'https://www.mercari.com/', 'params': {}},
    # {'name': 'AbemaTV', 'url': 'https://abema.tv/', 'params': {}},
    # {'name': 'Cookpad', 'url': 'https://cookpad.com/', 'params': {}},
    # {'name': 'Niconico', 'url': 'https://www.nicovideo.jp/', 'params': {}},
    # {'name': 'Oricon', 'url': 'https://www.oricon.co.jp/', 'params': {}},
    # {'name': 'Tabelog', 'url': 'https://tabelog.com/', 'params': {}},
    # {'name': 'Naver Japan', 'url': 'https://www.naver.jp/', 'params': {}},
    # {'name': 'Gree', 'url': 'https://gree.jp/', 'params': {}},
    # {'name': 'Baidu Japan', 'url': 'https://www.baidu.jp/', 'params': {}},
    # {'name': 'Daum Japan', 'url': 'https://www.daum.jp/', 'params': {}},
    # {'name': 'Ameba', 'url': 'https://www.ameba.jp/', 'params': {}},
    # {'name': 'FC2 Blog', 'url': 'https://blog.fc2.com/', 'params': {}},
    # {'name': 'Nobita', 'url': 'https://nobita.vn/', 'params': {}},
    # {'name': 'Hallogram', 'url': 'https://hallogram.com.ua/', 'params': {}},
    # {'name': 'Yado', 'url': 'https://yado.com.ua/', 'params': {}},
    # {'name': 'Tokyostudio', 'url': 'https://tokyostudio.com.ua/', 'params': {}},
    # {'name': 'Techium', 'url': 'https://techium.com.ua/', 'params': {}},
    # {'name': 'Codegym', 'url': 'https://codegym.com.ua/', 'params': {}}




    # Додайте більше сайтів для пошуку тут
]

for query in queries:
    modified_query = random_case(query)

    # Пошук на основних пошукових двигунах
    for search_engine in search_engines:
        if 'params' in search_engine:
            search_engine['params']['q'] = modified_query

    # Пошук на додаткових сайтах
    for site in additional_sites:
        search_engine = site.copy()
        search_engine['params']['q'] = modified_query
        search_engines.append(search_engine)

    search_with_timeout(query, search_engines, timeout)

# Обробка результатів з файлу pornhub_results.txt
process_pornhub_results()
