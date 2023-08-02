# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from hashlib import md5


class NtvArticleDefaultValuesPipeline:
    def process_item(self, item, spider):
        for key, default_value in item.default_values.items():
            item.setdefault(key, default_value)

        return item
    

class GeneratingArticleURNPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        headline = adapter.get('headline')
        updated = adapter.get('updated')
        url = adapter.get('updated')

        if headline and updated:
            concat_strs = headline + updated
            # md5 gives stable hash for strings
            adapter['urn'] = int(md5(concat_strs.encode('utf-8')).hexdigest(), 16)
            return item
        else:
            raise DropItem(f"Missing headline or updated in {item}\n"
                           f"URL: {url}")
            
