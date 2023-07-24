# Scrape all articles from https://reforum.io/tag/obshhestvo/. 
# Title, text, authors, tags, date posted, link. Save into CSV file

# find max pages
# for page in max_pages:
    # try:
        # get page html html
        # get all article links
        # for article in article_links:
            # try:
                # get article
                # find Title, text, authors, tags, date poste
                # add to results_list
            # except:
                # record Error on article
                # continue loop
    # except:
        # record error on {page}, continue loop

from bs4 import BeautifulSoup
from requests import get
from helpers import get_max_pages, get_article_urls, get_articles_data
import logging
import pprint

import csv


tag = 'obshhestvo'
articles_page_url = f'https://reforum.io/tag/{tag}/'
max_pages = get_max_pages(articles_page_url)
scraped_data = []

article_urls = get_article_urls(tag, max_pages)

# debug
j = len(article_urls) // 5
article_urls = article_urls[:j]

scraped_data = get_articles_data(article_urls)    

# write into csv
header = ['title', 'text', 'authors', 'tags', 'date_published', 'url']
with open('articles.csv', 'w', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=header, lineterminator='\n')
    writer.writeheader()
    for row in scraped_data:
        writer.writerow(row)


