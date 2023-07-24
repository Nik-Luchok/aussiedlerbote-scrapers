from bs4 import BeautifulSoup
from requests import get
import logging
from time import sleep
from pprint import pprint
import random


def get_max_pages(url: str) -> int | None:
    response = get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'lxml')
        sibling_element = soup.find('span', attrs={'class': 'page-numbers dots'})
        return int(sibling_element.find_next_sibling('a', attrs={'class': 'page-numbers'}).text)
    else:
        print(response.status_code)
        print(response.text)
        return None
    
    
def get_article_urls(tag, max_pages) -> list[str] :
    article_urls = []
    for page_num in range(1, max_pages):
        sleep(2)
        print(f"Getting {page_num}/{max_pages} url")
        # get page
        articles_page_url = f'https://reforum.io/tag/{tag}/page/{page_num}/'
        response = get(articles_page_url)
        if not response.ok:
            logging.error(response.status_code)
            logging.error(response.headers)
            continue
        
        # 
        soup = BeautifulSoup(response.text, 'lxml')
        links_parent_elements = soup.find_all('h2', attrs={'class': 'entry-title heading-size-1'})

        for parent in links_parent_elements:
            article_urls.append(parent.findChild(name='a').get(key='href'))

    return article_urls


def get_articles_data(urls: list[str]) -> list[dict]:
    articles = []

    for i, article_url in enumerate(urls):
        # to not overload site and get caught/banned
        sleep((max(random.gauss(3,1),2)))

        # progress
        print(f"Getting {i}/{len(urls)} article content")


        response = get(article_url)
        if not response.ok:
            logging.error(f'\n[Response status]: {response.status_code}\n',
                          f'\n[Response text]: {response.text}\n',
                          f'\n[Article Url]: {article_url}\n',
                          )
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        article_element = soup.find('article')

        # parce article
        title = article_element.find('h1', attrs={'class': 'entry-title'}) \
                               .get_text(separator='', strip=True)
        
        text = article_element.find('div', attrs={'class': 'post-inner thin'}) \
                              .get_text(separator='') 
        
        authors = article_element.find('li', attrs={'class': 'post-author'}) \
                                 .get_text(separator=':;', strip=True) \
                                 .split(':;')
        
        tags = article_element.find('li', attrs={'class': 'post-tags'}) \
                              .find('span', attrs={'class': 'meta-text'}) \
                              .get_text(separator='', strip=True) \
                              .split(',')
        
        date_published = article_element.find('li', attrs={'class': 'post-date'}) \
                                        .find('span', attrs={'class': 'meta-text'}) \
                                        .get_text(separator='', strip=True) 
        
        # assemble article
        article = {
            'title': title,
            'text': text,
            'authors': authors,
            'tags': tags,
            'date_published': date_published,
            'url': article_url,
        }

        articles.append(article)
    return articles


        
    

# test
if __name__ == "__main__":
    urls = ['https://reforum.io/blog/2023/07/02/putin-boitsya-silnee-chem-srednestatisticheskij-diktator/']
    articles_data = get_articles_data(urls)
    pprint(articles_data)
    