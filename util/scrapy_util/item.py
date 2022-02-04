import scrapy


class BriefItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    def __str__(self):
        d = {}
        for k, v in self.items():
            d[k] = str(v)[:20]
        return str(d)
