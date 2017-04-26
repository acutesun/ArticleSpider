# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        print('in ArticlespiderPipeline')
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):  # 不知道results什么结构类型, 可以打断点调试
        # results 是一个列表[(True, {'path': '..'})]
        for ok, dicts in results:
            item['front_image_path'] = dicts['path']  # 将图片路径保存到item的path中
        return item


class JsonWithExporterPipeline(object):
    # 调用scrapy提供的json exporter导出json文件
    def __init__(self):
        self.file = open('article.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=True)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    def __init__(self):

        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'root', 'article', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # 执行具体的插入
        insert_sql = 'insert into jobbole(url_object_id, title, url, create_time) VALUES (%s, %s, %s, %s)'
        a, b, c, d = item['url_object_id'], item['title'], item['url'], item['create_time']
        print(a, b, c,d)
        self.cursor.execute(insert_sql, (a, b, c, d))
        # self.cursor.execute('select * from jobbole')
        self.conn.commit()
        return item


class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            use_unicode=True,
            cursorclass=MySQLdb.cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error)
        return item

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # insert_sql = '''
        #                 insert into jobbole(url_object_id, title, url, create_time)
        #                 VALUES (%s, %s, %s, %s)
        #  '''
        # cursor.execute(insert_sql, (item['url_object_id'], item['title'], item['url'], item['create_time']))

        insert_sql = 'insert into jobbole(url_object_id, title, url, create_time) VALUES (%s, %s, %s, %s)'
        a, b, c, d = item['url_object_id'], item['title'], item['url'], item['create_time']
        print(a, b, c, d)
        cursor.execute(insert_sql, (a, b, c, d))
