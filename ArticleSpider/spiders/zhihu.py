# -*- coding: utf-8 -*-
from collections import namedtuple
import scrapy
import re
import time
import json
from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
from datetime import datetime


class ZhihuSpider(scrapy.Spider):
    # 配置单独的settings, 优先级高于settings文件中配置参数, 会覆盖settings配置参数
    custom_settings = {
        'COOKIES_ENABLED': True
    }
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit',
        'Host': 'www.zhihu.com',
        'Origin': 'https: // www.zhihu.com',
        'Referer': 'https: // www.zhihu.com /',
    }

    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D." \
                       "is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Crev" \
                       "iewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_" \
                       "settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_au" \
                       "thor%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blockin" \
                       "g%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbe" \
                       "st_answerer%29%5D.topics&limit={1}&offset={2}"

    def parse(self, response):
        pass

    def parse_all_url(self, response):   # 获取当前页面所有的url
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse_all_url)
                pass

    def start_requests(self):   # spider入口函数, 直接请求知乎登录界面
        return [scrapy.Request(url='https://www.zhihu.com/#signin',
                               headers=self.headers, callback=self.gen_captcha)]  # 回调login

    def get_xsrf(self, response):  # 获取_xsrf字段
        xsrf = re.match('[\w\W]*name="_xsrf" value="(.*?)"', response.text)
        xsrf = xsrf.group(1) if xsrf else ''
        return xsrf

    def gen_captcha(self, response):  # 异步请求验证码url
        _xsrf = self.get_xsrf(response)    # 在这里处理_xsrf, 此时的response还是start_request请求返回的response
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?{0}&type=login'.format(t)
        yield scrapy.Request(captcha_url, headers=self.headers,
                             meta={'_xsrf': _xsrf}, callback=self.login)

    def get_captcha(self, response):  # 下载并获取验证码图片
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
        from PIL import Image
        try:
            img = Image.open('captcha.jpg')
            img.show()
            img.close()
        except:
            raise
        captcha = input('输入验证码\n>')
        return captcha

    def login(self, response):
        _xsrf = response.meta.get('_xsrf', '')
        if not _xsrf:
            raise ValueError('_xsrf is null')
        captcha = self.get_captcha(response)
        post_data = {
            'phone_num': '13281208165',
            'password': '123456..',
            '_xsrf': _xsrf,
            'captcha': captcha,
        }
        post_url = 'https://www.zhihu.com/login/phone_num'
        return [scrapy.FormRequest(url=post_url, formdata=post_data,
                                 headers=self.headers, callback=self.check_login)]

    def check_login(self, response):    # 通过服务器返回的数据判断是否登录成功
        text_json = json.loads(response.text)
        if 'msg' in text_json and text_json['msg'] == '登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers, callback=self.parse_all_url)
                # dont_filter表示该请求不应被调度程序过滤.当您要多次执行相同的请求时使用此选项,以忽略重复的过滤器, 请谨慎使用,否则您将进入爬行循环
        else:

            raise RuntimeError(text_json['msg'])

    def parse_question(self, response):

        question_id = 0
        match = re.match(r'(.*?/question/(\d+))(/|$).*', response.url)
        if match:
            question_id = int(match.group(2))
        loader = ItemLoader(ZhihuQuestionItem(), response=response)
        loader.add_value('zhihu_id', question_id)   # 问题id
        loader.add_css('topics', '.QuestionHeader-topics .Popover div::text')  # 话题
        loader.add_value('url', response.url)  # 问题url
        loader.add_css('title', '.QuestionHeader-content .QuestionHeader-main .QuestionHeader-title::text')  # 问题标题
        loader.add_css('content', '.QuestionRichText .RichText::text')  # 问题的内容. 有可能为空
        loader.add_css('answer_num', '.List-headerText span::text')  # 问题回答数量
        loader.add_css('comments_num', '.QuestionHeader-actions button::text')  # 问题评论数量
        loader.add_css('watch_user_num', 'button .NumberBoard-value::text')  # 关注问题的用户
        loader.add_css('click_num', 'div.NumberBoard-item .NumberBoard-value::text')  # 问题浏览数量
        loader.add_value('crawl_time', datetime.now())  # 问题爬取时间
        item = loader.load_item()
        item['content'] = item['content'] if 'content' in item.keys() else None  # 需要给空值设置默认值
        yield item
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                            callback=self.parse_answer)



    def parse_answer(self, response):
        answers = json.loads(response.text)
        is_end = answers['paging']['is_end']
        next_url = answers['paging']['next']

        for answer in answers['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']  # 感觉是回答的id
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer["author"]["id"] if "id" in answer["author"] else None  # 可能为空
            answer_item['content'] = answer["content"] if "content" in answer else None  # 可能为空
            answer_item['praise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time'] = answer['created_time']
            answer_item['update_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.now()
            yield answer_item
        if not is_end:
            scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)


'''
1. 在知乎爬虫的入口函数请求知乎登录界面, 在完成请求响应后回调gen_captcha方法
2. 在gen_captcha方法中获取_xsrf字段, 这个是知乎发送给浏览器的, 需要同用户密码一同提交
3. 处理验证码相关逻辑, 并把得到_xsrf字段通过meta传递给login函数
4. 将得到的数据交给FormRequest请求, 并回调检查登录函数.check_login, 最后回调parse函数
5. 调用parse_all_url获取当前所有的问题url, 回调parse_question处理问题item. 并在问题提取所有的question链接
6. 将处理的question_item yield. 再请求answer的url并对answer_item进行处理.
7. 使用pipeline将数据异步插入数据库. 需要在对应的item（ZhihuQuestionItem, ZhihuAnswerItem）中构造sql语句插入需要的字段

    对代码进行调式可以将多余的请求注释掉, 提高调试效率,如调试zhihu_answer时将请求zhihu_question注释. 后面加上# debug方便后面查找取消
'''
