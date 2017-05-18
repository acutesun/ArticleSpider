# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import AticleItem, AticleItemLoader
from ArticleSpider.utils import common
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from selenium import webdriver
import os


class JobbolesSpider(scrapy.Spider):
    name = "jobboles"
    # allowed_domains = ["bolg.jobbole.com"]
    start_urls = ["http://blog.jobbole.com/all-posts"]

    def __init__(self):
        # self.browser = webdriver.Chrome(executable_path='/python/ArticleSpider/tools/chromedriver')
        super(JobbolesSpider, self).__init__()
        dispatcher.connect(self.close_chrome, signals.spider_closed)  # 当爬虫关闭时发送信号, 处理函数close_chrome执行

    def close_chrome(self):
        print('爬虫退出关闭chrome!')
        # self.browser.quit()

    def parse(self, response):
        print(response.text)
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')  # 1.获取当前页面的url图片url列表并交给scrapy下载
        for post_node in post_nodes:
            post_url = post_node.css('::attr(href)').extract_first()
            image_url = post_node.css('img::attr(src)').extract_first()     # 获取图片的url
            yield Request(url=parse.urljoin(response.url, post_url),        # 注意这里我暂时改为post_url，因为数据太多了。
                          meta={'front_image_url': image_url}, callback=self.parse_detail)

        next_url = response.css('.next.page-numbers::attr(href)').extract_first()  # 2. 获取下一页url列表并交给scrapy下载
        if next_url:
            print(parse.urljoin(response.url, next_url))
            yield Request(parse.urljoin(response.url, post_url), callback=self.parse)
            print('yield request')

    def parse_detail(self, response):

        front_image_url = response.meta.get('front_image_url', '')  # 获取文章封面图
        loader = AticleItemLoader(item=AticleItem(), response=response)
        loader.add_value('url_object_id', common.get_md5(response.url))
        loader.add_value('front_image_url', front_image_url)
        loader.add_value('url', response.url)
        loader.add_css('title', '.entry-header h1::text')
        loader.add_css('create_time', 'p.entry-meta-hide-on-mobile::text')
        loader.add_css('great_nums', '.post-adds .vote-post-up h10::text')
        loader.add_css('bookmark_nums', '.post-adds .bookmark-btn::text')
        loader.add_css('comment_nums', 'a[href="#article-comment"] span::text')
        loader.add_css('tags', 'p.entry-meta-hide-on-mobile a::text')
        loader.add_css('content', 'div.entry')
        item = loader.load_item()
        yield item

