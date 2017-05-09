import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re
import time

session = requests.session()  # 某一次连接(存放了服务器设置的cookie, 用来标识一个用户), requests每次调用会重新建立连接
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
try:
    session.cookies.load(ignore_discard=True)   # 加载保存的cookie, 直接登录
except:
    print('未能加载cookie！')

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit',
    'Host': 'www.zhihu.com',
    'Origin': 'https: // www.zhihu.com',
    'Referer': 'https: // www.zhihu.com /',
}


def is_login():  # 通过个人中心页面返回判断是否登录
    inbox_url = 'https://www.zhihu.com/inbox'
    response = session.get(inbox_url, headers=headers, allow_redirects=False)  # 不让重定向
    print('is_login:', response.status_code)
    if response.status_code != 200:
        return False
    else:
        return True


def get_xsrf():     # 获取_xsrf字段
    response = session.get('https://www.zhihu.com/', headers=headers)
    xsrf = re.match('[\w\W]*name="_xsrf" value="(.*?)"', response.text)
    if xsrf:
        return xsrf.group(1)
    else:
        return ''


def get_captcha():     # 获取验证码
    t = str(int(time.time()*1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?{0}&type=login'.format(t)
    # 这里只能使用session,因为这里的session存放了服务器设置给浏览器的cookie.如果是requests就会重新请求.导致cookie和服务器中设置的不匹配
    captcha_get = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(captcha_get.content)
    from PIL import Image
    try:
        img = Image.open('captcha.jpg')
        img.show()
        img.close()
    except:
        raise
    captcha = input('输入验证码\n>')
    return captcha


def zhihu_login(account, passwd):
    if re.match(r'^1\d{10}', account):
        user = 'phone_num'
        post_url = 'https://www.zhihu.com/login/phone_num'
    else:
        user = 'email'
        post_url = 'https://www.zhihu.com/login/email'

    post_data = {
        '{0}'.format(user): account,
        'password': passwd,
        '_xsrf': get_xsrf(),
        'captcha': get_captcha(),
    }

    response = session.post(post_url, data=post_data, headers=headers)
    session.cookies.save()  # 保存session中的cookie
    print(response.text)

if not is_login():
    zhihu_login('13281208165', '123456..')


'''
1. 分析登录的链接. 有两个一个是手机号登录(phone_num), 还有一个是邮箱登录(email)
2. 确定post的数据. 通过分析得到四个字段 account:账户 password:密码 _xsrf: 服务器发送过来的字段,可以get后用正则匹配得到
   captcha: 通过分析url得到图片的url连接, 由服务器随机生成。这里使用之前的建立会话的session对象访问验证码图片连接(因为
   session存放类服务器标识一个用户的cookie. 如果使用requests会重新设置cookie. 导致服务器以为是两个用户)
3. 保存cookie, 以后登录直接加载cookied登录, session.cookies.load(ignore_discard=True). 再通过个人中心页面返回判断是否登录
    如果没有成功加载cookie, 判断未登录状态, 则调用登录函数 zhihu_login
'''
