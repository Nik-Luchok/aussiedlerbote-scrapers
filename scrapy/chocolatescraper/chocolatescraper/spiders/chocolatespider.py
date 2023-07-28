import scrapy
from chocolatescraper.items import ChocolateProduct
from chocolatescraper.itemsloaders import ChocolcateProductLoader

import os
from urllib.parse import urlencode

PROXY_KEY = os.environ.get('PROXY_KEY')
PROXY_API_URL = os.environ.get('PROXY_API_URL')


def get_proxy_url(url):
    """Get proxy url leading to the website being scraped
    param: url
        url of the website to scrape
    """
    payload = {'api_key': PROXY_KEY, 'url': url}
    proxy_url = PROXY_API_URL + urlencode(payload)
    return proxy_url


class ChocolatespiderSpider(scrapy.Spider):
    name = "chocolatespider"

    def start_requests(self):
        start_url = 'https://www.chocolate.co.uk/collections/all'
        yield scrapy.Request(url=get_proxy_url(start_url), callback=self.parse)

    def parse(self, response):
        # take all products
        products = response.css('product-item')

        for product in products:
            chocolate = ChocolcateProductLoader(item=ChocolateProduct(), selector=product)
            chocolate.add_css('name', 'a.product-item-meta__title::text')
            chocolate.add_css('price','span.price', re='<span class="price">\n              <span class="visually-hidden">Sale price</span>(.*)</span>')
            chocolate.add_css('url', 'a.product-item-meta__title::attr(href)')
            yield chocolate.load_item()
            
        # crawl next page
        # next_page = response.css('[rel="next"] ::attr("href")').get()

        # if next_page is not None:
        #     next_page_url = "https://chocolate.co.uk" + next_page
        #     yield response.follow(get_proxy_url(next_page_url), callback=self.parse)
