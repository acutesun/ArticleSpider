from scrapy.cmdline import execute
import sys
import os


print(os.path.dirname(os.path.abspath(__file__)))  # /python/ArticleSpider/main.py
print(os.path.join(os.path.dirname(__file__), 'images'))    # /python/ArticleSpider/images
project_dir = os.path.abspath(os.path.dirname(__file__))
print(os.path.join(project_dir, 'images'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'jobboles'])
