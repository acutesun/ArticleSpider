# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re
import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst
from scrapy.loader import ItemLoader
from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from datetime import datetime
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    nums = int(match_re.group(1)) if match_re else 0
    return nums


def strip_all(strs):  # 取出Item 中的日期
    str_re = re.match(r'[\w\W]*?(\d{4}/\d{1,2}/\d{1,2})[\w\W]*?', strs)
    if str_re:
        return str_re.group(1)


def remove_tag(tag_list):
    return [e for e in tag_list if not e.strip().endswith('评论')]


class AticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()  # 设置每个Item的输出处理函数取列表中的第一个


class AticleItem(scrapy.Item):
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    front_image_url = scrapy.Field(  # 这里交给imagepipeline时必须是一个list
        output_processor=lambda x: list(x)  # 对传入的str转换成列表
    )
    front_image_path = scrapy.Field()
    title = scrapy.Field()
    create_time = scrapy.Field(
        input_processor=MapCompose(strip_all)
    )
    great_nums = scrapy.Field()
    bookmark_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    tags = scrapy.Field(
        input_processor=remove_tag,
        output_processor=Join(',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):  # 处理jobbole的插入
        insert_sql = 'insert into zhihu_question(url_object_id, title, url, create_time) VALUES (%s, %s, %s, %s)'

        params = ()
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):  # 知乎问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):  # 处理zhihu_question插入
        # 对实例对象的属性进行处理, question_item属性值都是列表
        zhihu_id = self['zhihu_id'][0]                      # int
        topics = ''.join(self['topics'])                    # str
        url = ''.join(self['url'])                          # str
        title = ''.join(self['title'])                      # str
        content = ''.join(self['content']) if self['content'] else None
        answer_num = get_nums(self['answer_num'][0])        # int
        comments_num = get_nums(self['comments_num'][0])    # int
        watch_user_num = get_nums(self['watch_user_num'][0])  # int
        click_num = get_nums(self['click_num'][0])          # int
        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)         # datetime
        crawl_update_time = datetime.now().strftime(SQL_DATETIME_FORMAT)
        # ON DUPLICATE KEY UPDATE 表示主键重复就更新给出的字段, 否则执行插入
        insert_sql = 'insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,' \
                     ' watch_user_num, click_num, crawl_time) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
                     'ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), ' \
                     'comments_num=VALUES(comments_num), watch_user_num=VALUES(watch_user_num), ' \
                     'click_num=VALUES(click_num), crawl_update_time=VALUES(crawl_update_time)'

        params =(zhihu_id, topics, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):  # 知乎回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):

        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)
        create_time = datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)

        insert_sql = 'insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num,' \
            ' comments_num, create_time, update_time, crawl_time) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ' \
            'ON DUPLICATE KEY UPDATE content=VALUES(content), praise_num=VALUES(praise_num), ' \
            'comments_num=VALUES(comments_num), create_time=VALUES(create_time), ' \
            'update_time=VALUES(update_time), crawl_update_time=VALUES(crawl_update_time)'
        params = (self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'].encode('utf-8'),
                  self['praise_num'], self['comments_num'], create_time, update_time, crawl_time)
        return insert_sql, params
