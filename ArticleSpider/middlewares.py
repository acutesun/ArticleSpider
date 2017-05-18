# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import time
from scrapy.http import HtmlResponse
import logging
from tools.user_agent import user_agent, browsers
from random import randint


logging.basicConfig(level=logging.DEBUG, datefmt='%a, %d %b %Y %H:%M:%S', filename='./ua.log', filemode='w')


class ArticlespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RUserAgentMiddleware(object):
    # 随机更换UA
    def __init__(self, crawler):
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if spider.name != 'zhihu':
            ua = user_agent[browsers[randint(0, 4)]][randint(0, 49)]
            request.headers.setdefault(b'User-Agent', ua)


class JSPageMiddleware(object):  # 需要在settings中配置生效

    def process_request(self, request, spider):  # 处理动态加载的网页

        if spider.name == 'jobboles':
            spider.browser.get(request.url)  # 使用spider创建的chrome动态加载js页面
            time.sleep(1)
            print('访问：{0}'.format(request.url))
            # 对已经交给chrome处理url返回, 不再交给downloader请求下载
            return HtmlResponse(url=spider.browser.current_url,
                                body=spider.browser.page_source, encoding='utf-8', request=request)
