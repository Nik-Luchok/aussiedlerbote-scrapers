# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DuplicatesPipeline:
    '''Check for duplicates by item's 'name' field'''

    def __init__(self) -> None:
        self.names_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter["name"] in self.names_seen:
            raise DropItem(f"Duplicate found at {item!r}")
        else:
            self.names_seen.add(adapter['name'])
            return item


class PriceToUSDPipeline:

    gbpToUsdRate = 1.3

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('price'):
            price = float(adapter['price'])
            adapter['price'] = price * self.gbpToUsdRate
            return item
        else:
            raise DropItem(f"Missing price in {item}")
