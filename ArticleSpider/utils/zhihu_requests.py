import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re
import time

session = requests.session()

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit',
    'Host': 'www.zhihu.com',
    'Origin': 'https: // www.zhihu.com',
    'Referer': 'https: // www.zhihu.com /',
}


def get_xsrf():     # 获取_xsrf字段
    response = requests.get('https://www.zhihu.com/', headers=headers)
    xsrf = re.match('[\w\W]*name="_xsrf" value="(.*?)"', response.text)
    if xsrf:
        return xsrf.group(1)
    else:
        return ''


def get_captcha():     # 获取验证码
    t = str(int(time.time()*1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?{0}&type=login'.format(t)
    captcha_get = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(captcha_get.content)
    pass

def zhihu_login(account, passwd):

    if re.match(r'^1\d{10}', account):
        post_url = 'https://www.zhihu.com/login/phone_num'
        datas={
            'phone_num': account,
            'password': passwd,
            '_xsrf': get_xsrf(),
            'captcha': ''
        }
        captcha = 'https://www.zhihu.com/captcha.gif?r=1494120591338&type=login'
        response = requests.post(post_url, data=datas, headers=headers)
        print(response.text)
        print(response.status_code)
    if '@' in account:
        print('邮箱登录')
        post_url = 'https://www.zhihu.com/login/email'
        requests.post(post_url, data='', headers=headers)

# zhihu_login('13281208165', '123456..')
get_captcha()