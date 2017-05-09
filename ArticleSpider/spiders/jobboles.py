# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import AticleItem, AticleItemLoader
from ArticleSpider.utils import common
from scrapy.loader import ItemLoader


class JobbolesSpider(scrapy.Spider):
    name = "jobboles"
    # allowed_domains = ["bolg.jobbole.com"]
    start_urls = ["http://blog.jobbole.com/all-posts"]

    def parse(self, response):

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

    # def parse_css(self, response):
    #     article_item = AticleItem()
    #     front_image_url = response.meta.get('front_image_url', '')  # 获取文章封面图
    #
    #     # css选择器提取信息 response.css().extract_first() 选取第一个
    #     title = response.css('.entry-header h1::text').extract_first()  # 选取所有包含entry-header的class元素下的h1元素的文本内容
    #     create_time = response.css('p.entry-meta-hide-on-mobile::text').extract_first()
    #     if create_time:
    #         create_time = create_time.strip().replace('·', '').strip()
    #
    #     great_nums = response.css('.post-adds .vote-post-up h10::text').extract_first('')   # 点赞
    #     if great_nums:
    #         great_nums = int(great_nums)
    #     else:
    #         great_nums = 0
    #
    #     bookmark_nums = response.css('.post-adds .bookmark-btn::text').extract_first('')    # 收藏
    #     bookmark_re = re.match(r'.*?(\d+).*', bookmark_nums)
    #     if bookmark_re:
    #         bookmark_nums = int(bookmark_re.group(1))
    #     else:
    #         bookmark_nums = 0
    #
    #     comment_nums = response.css('a[href="#article-comment"] span::text').extract_first('')  # 评论
    #     article_re = re.match(r'.*?(\d+).*', comment_nums)
    #     if article_re:
    #         comment_nums = int(article_re.group(1))
    #     else:
    #         comment_nums = 0
    #
    #     tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()    # 标签内容
    #     tag_list = [e for e in tag_list if not e.strip().endswith('评论')]
    #     tags = ','.join(tag_list)
    #
    #     content = response.css('div.entry').extract_first()[:100]   # 所有内容
    #
    #     article_item['url_object_id'] = common.get_md5(response.url)
    #     article_item['title'] = title
    #     article_item['url'] = response.url
    #     article_item['front_image_url'] = [front_image_url]
    #     article_item['create_time'] = create_time
    #     article_item['great_nums'] = great_nums
    #     article_item['comment_nums'] = comment_nums
    #     article_item['bookmark_nums'] = bookmark_nums
    #     article_item['tags'] = tags
    #     article_item['content'] = content
    #
    #     yield article_item  # 生成的item会传入到pipelines中


    # def parse_xpath(self, response):
    #
    #     # 标题
    #     title = response.xpath('//*[@id="post-110287"]/div[1]/h1/text()').extract()[0]
    #     # 创建时间
    #     create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()')[0].extract()
    #     # '\r\n\r\n            2017/02/18 ·  '  re.match(r'[\s\S]*(\d{4}/\d{1,2}/\d{1,2}).*', create_time)
    #     create_time = create_time.strip().replace('·', '').strip()
    #     # 点赞
    #     great_nums = int(response.xpath('//*[@data-post-id="110287"]/h10/text()').extract()[0])
    #     # 收藏
    #     bookmark = response.xpath('//span[contains(@class, "bookmark-btn")]/text()')  # span节点属性class的值里包含bookmark-btn
    #     # 评论
    #     article_comment = response.xpath('//*[@href="#article-comment"]/span/text()').extract()[0]
    #     re_match = re.match(r'.*?(\d+).*', article_comment)
    #     if re_match:
    #         article_comment = int(re_match.group(1))
    #     tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
    #     tag_list = [e for e in tag_list if not e.strip().endswith('评论')]
    #     tags = ','.join(tag_list)
