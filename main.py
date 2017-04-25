from scrapy.cmdline import execute
import sys
import os


print(os.path.dirname(os.path.abspath(__file__)))  # /python/ArticleSpider/main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'jobboles'])
