from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc

from n_tv.sitemap import TreeSitemap

import logging
from scrapy.http import Request
from scrapy.utils.sitemap import sitemap_urls_from_robots

import os
from urllib.parse import urlencode


logger = logging.getLogger(__name__)

PROXY_KEY = os.environ.get('PROXY_KEY')
PROXY_API_URL = os.environ.get('PROXY_API_URL')


def get_proxy_url(url):
    """Get proxy url that returns HTML page of url provided
    param: url
        url of the website to scrape
    """
    payload = {'api_key': PROXY_KEY, 'url': url}
    proxy_url = PROXY_API_URL + urlencode(payload)
    return proxy_url


class BaseSitemapSpider(SitemapSpider):
    # change Sitemap object. The default class doesn't provide 
    # the depth of most xml tree structures
    def _parse_sitemap(self, response):
        if response.url.endswith("/robots.txt"):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                logger.warning(
                    "Ignoring invalid sitemap: %(response)s",
                    {"response": response},
                    extra={"spider": self},
                )
                return

            # changed Sitemap class
            s = TreeSitemap(body)

            it = self.sitemap_filter(s)


            if s.type == "sitemapindex":

                for loc in iterloc(it, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == "urlset":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    for r, c in self._cbs:
                        if r.search(loc):
                            yield Request(loc, callback=c)
                            break
            # added additional information
            else:
                raise TypeError(f"s.type: {s.type} is not supported"
                                "Supported sitemap types: sitemapindex, urlset"
                                "if xml is rss(2) feed use XMLFeedSpider instead")
