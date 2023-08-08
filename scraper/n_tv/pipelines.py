# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from hashlib import md5
from n_tv.config import DBConfig
import psycopg
from psycopg.rows import dict_row

import logging


class DropDpaPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        for source in adapter['creditline']:
            if source.find("dpa") != -1:
                raise DropItem('dpa article')
        
        return item


class DuplicateOrUpdatedPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        article_html = adapter.get('article_html')
        url = adapter.get('url')

        if article_html and url:
            adapter['urn'] = md5(article_html.encode('utf-8')).hexdigest()
            url_hash = md5(url.encode('utf-8')).hexdigest()

            # check db
            with psycopg.connect(**DBConfig.params) as conn:
                with conn.cursor() as cursor:
                    cursor.row_factory = dict_row
                    cursor.execute("""
                                   SELECT *
                                   FROM article_hashes
                                   WHERE url_hash=%s;
                                   """, (url_hash, ))
                    
                    if cursor.rowcount:
                        # if url hash found in db
                        article_hash_old = cursor.fetchone()['article_hash']
                        if str(article_hash_old).replace('-', '') == adapter['urn']:
                            # if article hash equals value from db
                            raise DropItem("Duplicate")
                        
                        logging.info("Article updated, sending updated article")
                        
                        # set signal to 'sig:update'
                        adapter['signal'] = 'sig:update'

                    # update/set article hash in db
                    cursor.execute("""
                                    INSERT INTO article_hashes (url_hash, article_hash)
                                    VALUES (%s, %s);
                                    """, (url_hash, adapter['urn']))
                    return item

        else:
            raise DropItem(f"Missing article_html and url in {item}\n")
        

class NtvArticleDefaultValuesPipeline:
    def process_item(self, item, spider):
        for key, default_value in item.default_values.items():
            item.setdefault(key, default_value)

        return item
