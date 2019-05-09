

'''
初始化登录
'''
import json
import re
import subprocess
import sys
import time
from urllib import parse

import chardet
import requests
from gevent import os

captcha_path = os.path.join(os.getcwd(), "captcha")
if (not os.path.exists(captcha_path)):
    os.mkdir(captcha_path)
captcha_path = os.path.join(captcha_path, "telecom")
if (not os.path.exists(captcha_path)):
    os.mkdir(captcha_path)

def gen_image_name(name):
    return os.path.join(captcha_path, "{}.jpg".format(name))

def save_image(name, content):
    file_name = gen_image_name(name)
    with open(file_name, 'wb') as f:
        f.write(content)
    f.close()
    return file_name

def show_image(file_path):
    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', file_path])
    elif sys.platform.find('linux') >= 0:
        subprocess.call(['xdg-open', file_path])
    else:
        os.startfile(file_path)


headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://login.189.cn/web/login",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:46.0) Gecko/20100101 Firefox/46.0"
}

'''
1 访问图片验证码
2 输入验证码
'''
def check_captcha(name: str):
    mobile = '17793102135'

    s = requests.session()
    s.get(url='https://login.189.cn/web/login')
    resp = s.post(url="https://login.189.cn/web/login/ajax",
                         data=parse.urlencode({
                             "m": "checkphone",
                             "phone": mobile
                         }), headers=headers)
    content = resp.content
    encode_type = chardet.detect(content)  # 解决返回体编码的问题
    content = content.decode(encode_type['encoding'])
    content_dict = json.loads(content)
    provinceId = content_dict['provinceId']

    s.post(url="https://login.189.cn/web/login/ajax",
                         data=parse.urlencode({
                             "m": "captcha",
                             "account": mobile,
                             "uType": "201",
                             "ProvinceID": provinceId,
                             "areaCode": "",
                             "cityNo": ""
                         }), headers=headers)


    resp = s.get(url='https://login.189.cn/web/captcha?undefined&source=login&width=100&height=37&0.{value}'
                            .format(value=name))
    content = resp.content

    img_path = save_image(name, content)
    show_image(img_path)
    predict = input("please input image:")
    # predict = '1111'

    form_data = parse.urlencode({
        "Account": mobile,
        "UType": "201",
        "ProvinceID": provinceId,
        "AreaCode": "",
        "CityNo": "",
        "RandomFlag": "0",
        "Password": "BPtW2ckb3a1UBvwXphnKJQ==",
        "Captcha": predict
    })
    resp = s.post(url='https://login.189.cn/web/login', data=form_data, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:46.0) Gecko/20100101 Firefox/46.0",
        "Referer": "https://login.189.cn/web/login",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
    })
    content = resp.content
    encode_type = chardet.detect(content)  # 解决返回体编码的问题
    content = content.decode(encode_type['encoding'])

    pattern = re.search(r'data-resultcode="(\d+)"\s*data-errmsg="([\s\S]+?)"', str(content), re.M | re.I)
    code = pattern.group(1)
    msg = pattern.group(2)
    print("code:{code} \t msg:{msg}".format(code=code, msg=msg))
    if code == '9115':
        print("{captcha} 不正确".format(captcha=predict))
        os.rename(img_path, gen_image_name("{predict}-error".format(predict=predict)))
    else:
        print("{captcha} 正确".format(captcha=predict))
        os.rename(img_path, gen_image_name(predict))

    s.close()


while True:
    ## 时间戳
    name = str(int(round(time.time() * 1000)))
    check_captcha(name)