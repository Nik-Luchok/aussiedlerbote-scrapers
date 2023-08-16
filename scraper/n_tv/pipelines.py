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
from psycopg import sql

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
        # TODO refactor
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

                    # create dynamic sql query
                    domain_name = spider.domain_name
                    logging.warning(f"spider: {spider}, domain_name: {domain_name}")
                    q = sql.SQL("""SELECT * 
                                   FROM {domain_name_hashes_table} 
                                   WHERE url_hash=%s;""").format(
                                        domain_name_hashes_table=sql.Identifier(f"{domain_name}_article_hashes")
                                        )

                    cursor.execute(query=q, params=(url_hash, ))
                    
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
                    q = sql.SQL("""
                                INSERT INTO {domain_name_hashes_table} (url_hash, article_hash)
                                VALUES (%s, %s);
                                """).format(
                                    domain_name_hashes_table=sql.Identifier(f"{domain_name}_article_hashes")
                                    )
                    cursor.execute(query=q, params=(url_hash, adapter['urn']))
                    return item

        else:
            raise DropItem(f"Missing article_html and url in {item}\n")
        

class DefaultValuesPipeline:
    def process_item(self, item, spider):
        for key, default_value in item.default_values.items():
            item.setdefault(key, default_value)

        return item
