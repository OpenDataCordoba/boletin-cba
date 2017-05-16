# -*- coding: utf-8 -*-
import scrapy
import dateparser


class BoeSpider(scrapy.Spider):
    name = "boe"
    allowed_domains = ["boletinoficial.cba.gov.ar"]
    start_urls = ['http://boletinoficial.cba.gov.ar/']

    def parse(self, response):
        for grupo in response.xpath('//*[@id="container_portada"]/div/ul'):
            fecha = grupo.xpath('preceding::div[1]/text()').extract_first()
            date = dateparser.parse(fecha, languages=['es'])
            for seccion in grupo.xpath('li/a'):
                url = seccion.xpath('@href').extract_first()
                yield {
                    'fecha': fecha,
                    'date': date.strftime('%Y-%m-%d'),
                    'titulo': seccion.xpath('h2/text()').extract_first().strip(),
                    'url': url,
                    'file_urls': [url]
                }

        other_pages = response.xpath('//*[@id="archives_calendar-2"]/div/div/div/div/a/@href').extract()
        for next_page in other_pages:
            yield scrapy.Request(next_page, callback=self.parse)
