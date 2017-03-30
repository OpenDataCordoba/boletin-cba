# -*- coding: utf-8 -*-
import scrapy


class BoeSpider(scrapy.Spider):
    name = "boe"
    allowed_domains = ["boletinoficial.cba.gov.ar"]
    start_urls = ['http://boletinoficial.cba.gov.ar/']

    def parse(self, response):
        page = response.url.split("/")[-2]
        pdf_links = response.xpath('//*[@id="container_portada"]/div/ul/li/a/@href').extract()
        # self.log(pdf_links)
        for i, p in enumerate(pdf_links):
            pass
            # yield {'name': 'test', 'i': i, 'file_urls': [p]}
        self.log(response.url)
        other_pages = response.xpath('//*[@id="archives_calendar-2"]/div/div/div/div/a/@href').extract()
        for next_page in other_pages:
            yield scrapy.Request(next_page, callback=self.parse)
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
