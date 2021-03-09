import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sfil.items import Article


class SfilSpider(scrapy.Spider):
    name = 'sfil'
    start_urls = ['https://sfil.fr/actus/']

    def parse(self, response):
        links = response.xpath('//div[@class="article_title row"]/h3//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="article_title"]/h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h3[@class="titremeta"]/text()').get()
        if date:
            date = " ".join(date.split('|')[0].strip().split()[2:])

        content = response.xpath('//div[@class="article_post"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
