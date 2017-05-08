# -*- coding: utf-8 -*-
import scrapy
from collections import namedtuple
import re
import time
import json


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit',
        'Host': 'www.zhihu.com',
        'Origin': 'https: // www.zhihu.com',
        'Referer': 'https: // www.zhihu.com /',
    }

    User = namedtuple('User', ['account', 'passwd'])
    user = User('', '')

    def parse(self, response):
        with open('1.html', 'wb') as f:
            f.write(response.body)
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
        yield scrapy.FormRequest(url=post_url, formdata=post_data,
                                 headers=self.headers, callback=self.check_login)

    def check_login(self, response):    # 通过服务器返回的数据判断是否登录成功
        text_json = json.loads(response.text)
        if 'msg' in text_json and text_json['msg'] == '登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)


    def get_account(self):
        self.user.account = '13281208165'
        self.user.passwd = '123456..'
