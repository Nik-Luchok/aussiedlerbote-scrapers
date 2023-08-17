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


class DefaultValuesPipeline:
    def process_item(self, item, spider):
        for key, default_value in item.default_values.items():
            item.setdefault(key, default_value)

        return item
    

class DropDpaPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        for source in adapter['creditline']:
            if source.find("dpa") != -1:
                raise DropItem('dpa article')
        
        return item


class DuplicateOrUpdatedPipeline:
    """
    This pipeline hashes url and article_html and
    compares them with hashes stored in PostrgeSQL db.

    If url is already seen we check article hash
    and drop the article or set 'signal' to 'sig:update"
    to mark it as updated.
    """
    def process_item(self, item, spider):
        # set adapter and get some item values
        adapter = ItemAdapter(item)
        article_html = adapter.get('article_html')
        url = adapter.get('url')
        domain_name = spider.domain_name

        if article_html and url:
            # get 32char hex string hash of article and url
            adapter['urn'] = article_hash = self._get_hash(article_html)
            url_hash = self._get_hash(url)

            # open postgresql db connection
            with psycopg.connect(**DBConfig.params) as conn:
                with conn.cursor() as cursor:
                    # configure cursor
                    cursor.row_factory = dict_row

                    if self._is_article_duplicate(domain_name, cursor, url_hash):
                        self._drop_duplicate_or_mark_updated(cursor, adapter, article_hash)

                    if adapter['signal'] == 'sig:update':
                        self._update_hashes_in_db(domain_name, cursor, url_hash, article_hash)
                    else:
                        self._insert_hashes_in_db(domain_name, cursor, url_hash, article_hash)

                    return item
        else:
            raise DropItem(f"Missing article_html or url in {item['url']}\n")
        
    def _get_hash(self, string: str) -> str:
        """get stable hash of string"""
        return md5(string.encode('utf-8')).hexdigest()
          
    def _is_article_duplicate(self, domain_name, cursor, url_hash) -> bool:
        """query db and check if url hash matches with any"""
        # create dynamic sql query
        q = sql.SQL("""SELECT * 
                       FROM {table}
                       WHERE url_hash=%s;""").format(
            table=sql.Identifier(f"{domain_name}_article_hashes")
        )      

        # query db
        cursor.execute(query=q, params=(url_hash, ))
        return cursor.rowcount != 0

    def _drop_duplicate_or_mark_updated(self, cursor, adapter, article_hash):
        article_hash_old = self._get_old_article_hash(cursor)
        if article_hash_old == article_hash:
            raise DropItem("Duplicate")
        
        # 'sig:update' marks that article was updated
        logging.info("Article updated, sending updated article")
        adapter['signal'] = 'sig:update'
    
    def _get_old_article_hash(self, cursor):
        """gets 'article_hash' postgre UUID object from cursor, 
        serializes it to 32char alphanumerical hex string"""
        article_hash_old = cursor.fetchone()['article_hash']
        return str(article_hash_old).replace('-', '')
    
    def _update_hashes_in_db(self, domain_name, cursor, url_hash, article_hash):
        q = sql.SQL("""
                    UPDATE {table}
                    SET article_hash = %s
                    WHERE url_hash = %s;""").format(
            table=sql.Identifier(f"{domain_name}_article_hashes")
        )
        cursor.execute(query=q, params=(article_hash, url_hash))

    def _insert_hashes_in_db(self, domain_name, cursor, url_hash, article_hash):
        q = sql.SQL("""
                    INSERT INTO {table} (url_hash, article_hash)
                    VALUES (%s, %s);""").format(
            table=sql.Identifier(f"{domain_name}_article_hashes")
        )
        cursor.execute(query=q, params=(url_hash, article_hash))

