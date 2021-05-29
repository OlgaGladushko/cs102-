import requests
from bs4 import BeautifulSoup
from db import News, session


def extract_news(parser):
    """ Extract news from a given web page """
    news_list = []

    table = (parser.find('table', {'class': 'itemlist'}))
    trs = table.find_all("tr")
    count = 0
    dict_add = {
        'author': None,
        'comments': 0,
        'points': 0,
        'title': None,
        'url': None
    }
    
    for i, elem in enumerate(trs):
        if i < 90:
            if count == 0:
                dict_add["title"] = elem.find('a', {'class': 'storylink'}).get_text()
                dict_add['url'] = (elem.find('a', {'class': 'storylink'}))['href']
            if count == 1:
                str_point=(elem.find('span', {'class': 'score'})).get_text()
                dict_add['points'] = int(str_point[:str_point.find(" ")])
                dict_add['author'] = elem.find('a', {'class': 'hnuser'}).get_text()
                a_els = elem.find_all("a")
                if a_els[-1].get_text() == "discuss":
                    dict_add['comments'] = 0
                else:
                    str_comm = a_els[-1].get_text()
                    dict_add['comments'] = int(str_comm[:str_comm.find(" ")])
            if count == 2:
                news_list.append(dict_add)
                count = -1
                dict_add = {
                    'author': None,
                    'comments': 0,
                    'points': 0,
                    'title': None,
                    'url': None
                }
            count += 1

    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    table = (parser.find('table', {'class': 'itemlist'}))
    trs = table.find_all("tr")
    return trs[-1].find('a', {'class': 'morelink'})['href']


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
        print(len(news))
        
    return news
