# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import sqlalchemy.exc

from .database.connection import db
from .database.models import SeccionBoletin


class BoescraperPipeline(object):

    def process_item(self, item, spider):
        file_path = None
        try:
            file_path = item['files'][0]['path']
        except KeyError as e:
            logging.debug(item['files'][0]['path'])

        record = SeccionBoletin(
            titulo=item['titulo'],
            date=item['date'],
            url=item['url'],
            file_path=file_path,
        )
        try:
            db.add(record)
            db.commit()
        except sqlalchemy.exc.IntegrityError as err:
            logging.debug('Skip %s seccion %s' % (item['date'], item['titulo']))
            db.rollback()

        return item