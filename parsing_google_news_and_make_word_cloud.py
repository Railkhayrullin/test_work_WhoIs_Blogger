# for work part 1: "google.news parsing"
from bs4 import BeautifulSoup
import requests
import re
from random import choice
from multiprocessing import Pool
from time import sleep

# for work part 2: "text_analyse_and_make_word_cloud"
import gensim
from gensim.utils import simple_preprocess
from nltk import FreqDist
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# ____________________________________________ 1. google.news parsing ____________________________________________
def get_proxy():
    print('parsing a proxy list...')
    try:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/81.0.4044.129 Safari/537.36 OPR/68.0.3618.63'}
        url_pattern = 'https://hidemy.name/ru/proxy-list/?type=hs&start={}#list/'
        proxy_list = []
        for i in range(0, 704, 64):
            url = url_pattern.format(i)
            r = requests.get(url, headers=header, timeout=3)
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            trs = soup.find('div', class_="table_block").find('tbody').find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                schema = 'https' if 'HTTPS' in tds[4].text.strip() else 'http'
                proxy = {'schema': schema, 'address': ip + ':' + port}
                proxy_list.append(proxy)
        print('proxy_list "ok"')
        return proxy_list
    except requests.exceptions.ConnectionError:
        print('get_proxy ConnectionError')


def choice_proxy(list_proxy):
    p = choice(list_proxy)
    proxy = {p['schema']: p['address']}
    return proxy


def get_url():
    url_pattern = 'https://www.google.com/search?q=Russia&newwindow=1&client=opera&tbas=0&tbs=qdr:m&tbm=nws&ei=D' \
                  'nCWX57fCqetrgTKnaXABw&start={}&sa=N&ved=0ahUKEwientH609HsAhWnlosKHcpOCXg4FBDy0wMIgwE&biw=' \
                  '1880&bih=939&dpr=1/'
    url_list = []
    for i in range(20):
        a = i * 10
        url = url_pattern.format(a)
        url_list.append(url)
    print('url_list "ok"')
    return url_list


def get_all(url_list, proxy_list):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36 OPR/68.0.3618.63',
              'Cookie': 'S=billing-ui-v3=WfZtvc4sUHLwo7orkaOuLefa3AvdUWzQ:billing-ui-v3-efe=WfZtvc4sUHLwo7orkaOuLef'
                        'a3AvdUWzQ; HSID=AYIAe1bjwCXSSTDdD; SSID=AQDg6WRf0VSa0p185; APISID=o-SX0yrrH6QUKOd9/AsZdyeh'
                        'TEPZj12z7M; SAPISID=-6xloCOm9wjmFLaf/AOBaWx733xtW-PJFG; __Secure-3PAPISID=-6xloCOm9wjmFLaf/A'
                        'OBaWx733xtW-PJFG; ANID=AHWqTUn-EF1bY_AbMuPRa07DKI8MB3HgB1raMVl4PqK8m2J0OxYqZfBSt5VvA9uA; SID'
                        '=2wfYYfvf0c6z0yzS30PBm1Z1b4_Awqu6j9kWsLnMLTrXxIKRw7UQ9-EW9fetRr2fkVLLmg.; __Secure-3PSID=2wf'
                        'YYfvf0c6z0yzS30PBm1Z1b4_Awqu6j9kWsLnMLTrXxIKRr_O_aWzx-pfjcnJjoVDfnw.; 1P_JAR=2020-10-26-06;'
                        ' NID=204=GhtnpUXKFNP2BVL8-b-d3w7HBuMmqGOusubwz9KGrAZOkXcP_tri25oFRu75cyvQZ03Nevk7nIHt0vJXQQ'
                        '4oGd9n-LRaqQRZBYNL5LegLSrTk68YDyi7kUC_aFJbXuq1dbOA31GcDlbM3QvpnmpS-tKz2EmhSRKVD9QIO1h5zDbOxo'
                        'ygR5eqz311XNYHqLTKYqA6Z9WVVPcmPdZqg0-51hR0S9L0cB-QTongWh8nDGXea1YFDOTMssSwbQeIJ4dzHYcx5rBCDc'
                        'wjnF2IVxaI1-W20Lk-yM15ZzbEuJDM2vqr6NsS0-AdYE5k1Yxv8jcdJQf2cB-QIhGsuyqwR--heNo8f28; SIDCC=AJi'
                        '4QfECo3jjaug_eehVnT6cd-m-UmPpJ9UhGUVeAHJUdV4FPJwKUPJkwNsRr_nSeN0PIYBI3BE; __Secure-3PSIDCC='
                        'AJi4QfGAo_Br4JXNX1Sh2jnBTgxZjkWm9cb-O7lIka_J5ZDH4UHTwIHGyP0faIdYswftmH3SI9o'}
    for url in url_list:
        try:
            proxy = choice_proxy(proxy_list)
            r = requests.get(url, headers=header, proxies=proxy, timeout=3)
            html = r.text
            links = get_links(html)
            make_pool(links)

        except requests.exceptions.ConnectionError:
            print('ConnectionError in get_all()')
        except requests.exceptions.ReadTimeout:
            print('ReadTimeout in get_all()')
        except OSError:
            print('ProxyError in get_all()')


def get_links(html):
    try:
        links = []
        soup = BeautifulSoup(html, 'lxml')
        divs = soup.find('div', id="rso").find_all('div', class_="dbsr")
        for div in divs:
            link = div.find('a').get('href')
            links.append(link)
        print('**links_list ok**')
        return links

    except TypeError:
        print('TypeError in get_links()')


def make_pool(links):
    try:
        with Pool(10) as p:
            p.map(get_data, links)

    except TypeError:
        print('TypeError in make_pool()')


def get_data(link):
    try:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/81.0.4044.129 Safari/537.36 OPR/68.0.3618.63',
                  'Accept-Language': 'q=0.9,en-US;q=0.8,en;q=0.7'}
        r = requests.get(link, headers=header, timeout=3).text
        soup = BeautifulSoup(r, 'lxml')
        soup_text = ' '.join(soup.text.split())
        text = text_clear(soup_text) + '\n'
        save_text(text)
        print('ok', end=' ')

    except IndentationError:
        print('get_data IndentationError')
    except requests.exceptions.ConnectionError:
        print('ConnectionError in func "get_links"')
    except requests.exceptions.ReadTimeout:
        print('get_data TimeoutError')


def text_clear(raw_text):
    pattern = re.compile(r"[^a-zA-Z[:'.\-,\] ]")
    text = pattern.sub('', raw_text)
    lower_text = text.lower()
    return lower_text


def save_text(text):
    try:
        with open('news_text.txt', 'a', encoding='utf-8') as f:
            f.write(text)
    except OSError:
        print('OSError in save_text()')


def main_of_parsing():
    print('*** part 1: google.news parsing ***')
    sleep(1)
    proxy_list = get_proxy()
    get_all(get_url(), proxy_list)
    print()
    print('*** part 1: DONE✓ ***')
    sleep(1)


# ______________________________________________ 2. text_analyse_and_make_word_cloud ______________________________


def get_text():
    with open('news_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r"\'", "", text)
        text = re.sub(r"russia\w+", "russian", text)
        text = re.sub(r"\bhong.kong\b", "hong_kong", text)
        text = re.sub(r"\b(united.states|u\.s.)", "united_states", text)
        text = re.sub(r"\b(donald.trump|trump)", "donald_trump", text)
        text = re.sub(r"last.year", "last_year", text)
        text = re.sub(r"years", "year", text)
        print('get_text() "ok"')
        return text


# removes punctuations
def sent_to_words(text):
    words = gensim.utils.simple_preprocess(str(text), deacc=True)
    print('sent_to_words() "ok"')
    return words


def remove_stopwords(text):
    stop_words = stopwords.words('english')
    stop_words.extend(['from', 'subject', 're', 'edu', 'used', 'see', 'said', 'also', 'made', 'new', 'could', 'day',
                       'may', 'taking', 'read', 'first', 'go', 'even', 'case', 'middle', 'know', 'get', 'come', 'say',
                       'campaign', 'said', 'searching', 'search', 'called', 'use', 'take', 'took', 'share', 'make',
                       'mediums', 'media', 'giving', 'good', 'best', 'better', 'former', 'followed', 'start',
                       'gone', 'went', 'gave', 'give', 'saw', 'seeing', 'become', 'became', 's', 'two', 'oct', 'mr',
                       'says', 'since', 'like', 'one', 'us', 'would', 'email', 'time', 'times', 'year', 'twitter',
                       'facebook', 'photos', 'news', 'days'])
    remove_stop = [word for word in simple_preprocess(str(text)) if word not in stop_words]
    print('remove_stopwords() "ok"')
    return remove_stop


def get_50_words(list_tokens):
    freq_dist = FreqDist(list_tokens)
    first_50 = freq_dist.most_common(50)
    first_50_tokens = [word[0] for word in first_50]
    print('get_50_words() "ok"')
    return first_50_tokens


def get_word_cloud(first_50_tokens):
    picture_of_cloud = 'first_50_words.png'
    cloud = WordCloud(background_color='white', mode='RGBA', width=1200, height=800).generate(' '.join(first_50_tokens))
    plt.figure(figsize=(12, 8))
    plt.imshow(cloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(picture_of_cloud)
    print('get_word_cloud() "ok"')


def main_of_text_analyse_and_make_word_cloud():
    print('*** part 2: text_analyse_and_make_word_cloud ***')
    sleep(1)
    data_words = sent_to_words(get_text())
    words_no_stop = remove_stopwords(data_words)
    first_50_words = get_50_words(words_no_stop)
    get_word_cloud(first_50_words)
    print('*** part 2: DONE✓ ***')


def main():
    main_of_parsing()
    main_of_text_analyse_and_make_word_cloud()


if __name__ == '__main__':
    main()
