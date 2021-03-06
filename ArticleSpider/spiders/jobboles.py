# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import AticleItem


class JobbolesSpider(scrapy.Spider):
    name = "jobboles"
    # allowed_domains = ["bolg.jobbole.com"]
    start_urls = ["http://blog.jobbole.com/all-posts"]

    def parse(self, response):
        print('parses.............')
        post_urls = response.css('#archive .floated-thumb .post-thumb a::attr(href)').extract()
        for post_url in post_urls:
            print(post_url)
            yield Request(url=post_url, callback=self.parse_css)
            print(post_url)


    def parse_css(self, response):
        print('parse_css.....')
        # article_item = AticleItem()

        # front_image_url = response.meta.get('front_image_url', '')  # 获取文章封面图

        # css选择器提取信息 response.css().extract_first() 选取第一个
        title = response.css('.entry-header h1::text').extract()  # 选取所有包含entry-header的class元素下的h1元素的文本内容
        create_time = response.css('p.entry-meta-hide-on-mobile::text').extract_first()
        if create_time:
            create_time = create_time.strip().replace('·', '').strip()
        # 点赞
        great_nums = response.css('.post-adds .vote-post-up h10::text').extract_first('')
        if great_nums:
            great_nums = int(great_nums)
        else:
            great_nums = 0
        # 收藏
        bookmark_nums = response.css('.post-adds .bookmark-btn::text').extract_first('')
        print(bookmark_nums)
        bookmark_re = re.match(r'.*?(\d+).*', bookmark_nums)
        if bookmark_re:
            bookmark_nums = int(bookmark_re.group(1))
        else:
            bookmark_nums = 0
        print(bookmark_nums)
        # 评论
        comment_nums = response.css('a[href="#article-comment"] span::text').extract_first('')
        article_re = re.match(r'.*?(\d+).*', comment_nums)
        if article_re:
            comment_nums = int(article_re.group(1))
        else:
            comment_nums = 0
        # 标签内容
        tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [e for e in tag_list if not e.strip().endswith('评论')]
        tags = ','.join(tag_list)
        # 所有内容
        content = response.css('div.entry').extract_first()


        # 将所有的值填充到item

        # article_item['url'] = response.url
        # article_item['front_image_url'] = front_image_url
        # article_item['create_time'] = create_time
        # article_item['great_nums'] = great_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['tags'] = tags
        # article_item['content'] = content

        # yield article_item  # 生成的item会传入到pipelines中


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
