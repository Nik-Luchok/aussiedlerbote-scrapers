from n_tv.base_spiders import get_proxy_url
from n_tv.itemsloaders import BildArticleLoader
from n_tv.items import DigitalWiresArticle

from scrapy.spiders import XMLFeedSpider

import logging


class BildRubricSpider(XMLFeedSpider):
    name = 'bildrubricspider'
    custom_settings = {
        'ITEM_PIPELINES': {
            'n_tv.pipelines.DefaultValuesPipeline': 100
        },
        'CONCURRENT_REQUESTS': 1
    }
    start_urls = ['https://www.bild.de/sitemap.xml']
    itertag = 'item'
    
    def parse_node(self, response, node):
        """
        Parcing sitemap.xml of rss2 format
        node - each 'item' tag in xml file

        return "command" for spider to parce article url
        and for each to call a parce_article() function
        """
        # Filter. sort out rules
        # TODO test when krieg ticker in sitemap.xml
        if (    self._is_dpa_article(node)
                or self._is_bild_plus_article(node)
                or self._is_ukraine_krieg_ticker(node)):
            return None
        

        # init item loader and save some metadata from rss feed to it
        article_loader = BildArticleLoader(item=DigitalWiresArticle(), selector=node)

        # keywords
        article_loader.add_xpath('keyword_names', 'category/text()')

        # date/time
        article_loader.add_xpath('dateline', 'pubDate/text()')
        article_loader.add_xpath('embargoed', 'pubDate/text()')
        article_loader.add_xpath('version_created', 'pubDate/text()')
        article_loader.add_xpath('updated', 'pubDate/text()')

        # article url
        article_loader.add_xpath('url', 'link/text()')

        # return response following callback next parse function
        url = article_loader.get_collected_values('url')[0]
        return response.follow(get_proxy_url(url),
                               callback=self.parse_article,
                               cb_kwargs={'article_loader': article_loader})
    
    @classmethod
    def _is_dpa_article(cls, node) -> bool:
        media_credit = node.xpath(
            '//media:credit/text()',
            namespaces={'media': 'http://search.yahoo.com/mrss/'}).get()
        
        if media_credit is None or media_credit.find('dpa') == -1:
            return False
        else: 
            return True
        
    @classmethod
    def _is_bild_plus_article(cls, node) -> bool:
        link = node.xpath('link/text()').extract_first()
        if link.find('bild-plus') != -1:
            return True
        else:
            return False
        
    @classmethod
    def _is_ukraine_krieg_ticker(cls, node) -> bool:
        link = node.xpath('link/text()').extract_first()
        if link.find('ukraine-krieg-die-aktuelle-lage-im-live-ticker') != -1:
            return True
        else:
            return False
    
    def parse_article(self, response, article_loader):
        """
        Parce scraped article with css selectors. 
        Save data via ArticleLoader
        
        """
        # save article item
        article = response.css("main.main-content article")
        article_loader.selector = article

        # parse header
        language = response.css("html::attr('lang')").get()
        keywords_str = response.css("[name='keywords']::attr('content')").get()
        
        # textual data
        article_loader.add_css('headline', "span.article-title__headline::text")
        article_loader.add_css('kicker', "span.article-title__kicker::text")
        article_loader.add_css('teaser', "div.article-body p b::text")

        self._clean_article(article)
        article_loader.add_css('article_html', "div.article-body")

        # metadata
        article_loader.add_value('language', language)

        # sources (No sourcees provided, hardcode 'bild')
        article_loader.add_value('creditline', "bild")
  
        # rubric, keywords, tags
        url = article_loader.get_collected_values('url')[0]
        article_loader.add_value('current_rubric_names', url)
        article_loader.add_value('rubric_names', url)
        article_loader.add_value('keyword_names', keywords_str)

        return article_loader.load_item()

    @classmethod
    def _clean_article(cls, article):
        """Clean article tag from useless tags, ads, scripts
        using drop() method of lxml tree elements. Learn more in lxml docs
        """
        # remove teaser
        article.css("div.article-body p")[0].drop()
        
        # remove all ads, recomendations
        article.css("div[data-ad-delivered]").drop()
        article.css("aside").drop() 

        # remove pictures
        article.css("figure").drop()