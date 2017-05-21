# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import subprocess
import os
import sqlalchemy.exc
from slugify import slugify

from .database.connection import db
from .database.models import SeccionBoletin

FILE_BASE = 'tmp'


def pdf2text(file_path):
    proc = subprocess.Popen(["pdftotext", '-raw', file_path, '-'], stdout=subprocess.PIPE,
        bufsize=1, universal_newlines=True)
    return ''.join([line for line in proc.stdout])


class BoescraperPipeline(object):

    def process_item(self, item, spider):
        file_path = None
        try:
            file_path = item['files'][0]['path']
        except KeyError as e:
            logging.debug(item['files'][0]['path'])

        if file_path:
            content = pdf2text(os.path.join(FILE_BASE, file_path))

        record = SeccionBoletin(
            titulo=item['titulo'],
            slug=slugify(item['titulo']),
            date=item['date'],
            url=item['url'],
            file_path=file_path,
            content=content,
        )
        try:
            db.merge(record)
            db.commit()
        except sqlalchemy.exc.IntegrityError as err:
            logging.debug('Skip %s seccion %s' % (item['date'], item['titulo']))
            db.rollback()

        return item
