# coding:utf-8
from time import time, sleep
from PIL import Image
import requests
import sys
import os
from bs4 import BeautifulSoup
import re
import PyV8

import urllib2
import urllib

reload(sys)
sys.setdefaultencoding('utf8')


# 检查存储路径是否正常
def check_path(_path):
    # 判断存储路径是否存在
    if os.path.isdir(_path) or os.path.isabs(_path):
        # 判断存储路径是否为空
        if not os.listdir(_path):
            return _path

        else:

            print u'>>>[-] 目标文件不为空，将清空目标文件，是否更换路径？'
            flag = raw_input('>>>[*] Yes:1 No:2 \n>>>[+] [2]')

            try:
                if flag == '1':
                    _path = raw_input(unicode('>>>[+] 请输入目标文件路径。\n>>>[+] ').encode('gbk'))
                    check_path(_path)
                else:
                    # 清空存储路径
                    os.system('rd /S /Q ' + _path)
                    os.system('mkdir ' + _path)
                    return _path
            except Exception as e:
                print e
                exit(0)

    else:
        os.makedirs(_path)
        return _path


# 功能：爬取m3u8格式的视频
# 获取ts视频的爬取位置
def get_url(_url, _path):
    all_url = _url.split('/')
    url_pre = '/'.join(all_url[:-1]) + '/'
    url_next = all_url[-1]

    os.chdir(_path)
    # 获取m3u8文件
    m3u8_txt = requests.get(_url, headers={'Connection': 'close'})
    with open(url_next, 'wb') as m3u8_content:
        m3u8_content.write(m3u8_txt.content)
    # 提取ts视频的url
    movies_url = []
    _urls = open(url_next, 'rb')
    for line in _urls.readlines():
        if '.ts' in line:
            # movies_url.append(url_pre + line[:-1])
            movies_url.append(line[:-1])
        else:
            continue

    _urls.close()
    return movies_url


# 爬取ts视频
def download_movie(movie_url, _path):
    os.chdir(_path)
    print '>>>[+] downloading...'
    print '-' * 60
    error_get = []

    for _url in movie_url:
        # ts视频的名称
        movie_name = _url.split('/')[-1][-6:]

        try:
            # 'Connection':'close' 防止请求端口占用
            # timeout=30    防止请求时间超长连接
            # movie = s.get(_url,timeout=60)
            movie = requests.get(_url, headers={'Connection': 'close'}, timeout=60)
            with open(movie_name, 'wb') as movie_content:
                movie_content.writelines(movie)
            print '>>>[+] File ' + movie_name + ' done'
        # 捕获异常，记录失败请求
        except:
            error_get.append(_url)
            continue
    # 如果没有不成功的请求就结束
    if error_get:
        print u'共有%d个请求失败' % len(file_list)
        print '-' * 60
        download_movie(error_get, _path)
    else:
        print '>>>[+] Download successfully!!!'


def mkdir(path):
    # 引入模块
    import os

    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        print path + ' 创建成功'
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path + ' 目录已存在'
        return False

if __name__=="__main__":
    s = requests.session()

    ctxt = PyV8.JSContext()
    ctxt.__enter__()

    html = urllib2.urlopen('http://cas.bnu.edu.cn/cas/comm/js/des.js').read()

    ctxt.eval(html)

    # 把strEnc绑定到js中的strEnc方法
    strEnc = ctxt.locals.strEnc

    url = 'http://cas.bnu.edu.cn/cas/login?service=http://one.bnu.edu.cn/dcp/index.jsp'

    # 获取lt
    html = s.get(url)

    bs = BeautifulSoup(html.text, "lxml")

    e = bs.find('input', id='lt')

    lt = e.attrs['value']
    # 构建cookie
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection	': 'keep-alive',
        'Content-Length': '367',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '_ga=GA1.3.1748768853.1489807370; Language=zh_CN; JSESSIONID=' + s.cookies.values()[0],
        'Host': 'cas.bnu.edu.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'Referer': 'http://cas.bnu.edu.cn/cas/login?service=http%3A%2F%2Fone.bnu.edu.cn%2Fdcp%2Findex.jsp'
    }

    # 账号密码
    u = '201411132033'

    p = '2010ccywsy'
    # 需要post的数据，其中有trides加密

    post_data = {

        '_eventId': 'submit',
        'execution': 'e1s1',
        'lt': lt,
        'pl': '10',
        'rememberMe': 'on',
        'rsa': strEnc(u + p + lt, '1', '2', '3'),
        'ul': '12'
    }
    postdata = urllib.urlencode(post_data)

    req = s.post('http://cas.bnu.edu.cn/cas/login?service=http://one.bnu.edu.cn/dcp/index.jsp', headers=headers,
                 data=postdata)

    print '登录状态：', req.status_code

    ##完成登录

    # _url = raw_input(unicode('>>>[+] 请输入指定的[.m3u8]目标URL。\n>>>[+] ').encode('gbk'))
    urlMovies = raw_input(unicode('>>>[+] 请输入指要下载的电视剧目标URL。\n>>>[+] ').encode('utf-8'))
    _path = raw_input(unicode('>>>[+] 请输入存储文件夹名字（英文）。\n>>>[+] ').encode('utf-8'))
    # _url = 'http://172.16.215.40:5320/uploads/video6/hls/b/d/5/f/bd5f4c03e0fccb0b79039bffd1334cbf/wl.m3u8'

    req2 = s.get(urlMovies)
    html2 = req2.content
    bs1 = BeautifulSoup(html2, 'lxml')
    tr = bs1.h3.a.attrs['title']
    # mkpath="d:/qttc/movies/"+'-'.join(tr.split('/'))
    mkpath = "d:/qttc/movies/" + _path
    mkdir(mkpath)
    hlist = bs1.find('ul', class_="nav nav-pills").find_all('a')
    hlist = ['http://532movie.bnu.edu.cn' + x.attrs['href'] for x in hlist]

    _path = mkpath
    i = 1
    for _url in hlist:
        try:
            req1 = s.get(_url)

            html = req1.content

            bs = BeautifulSoup(html, "lxml")

            txt = bs.find_all('script')[-1]

            a = re.search('playlist="[^"]*"', str(txt.text))

            str1 = a.group()

            str2 = str1.split('=')[1].split('+++')

            str3 = [x.strip('"') for x in str2]

            str3

            str3[0]

            preurl = "http://172.16.215.40:5320/"

            downfilm = preurl + str3[0]
            # _url=downfilm
            # storage_path = check_path(_path)
            storage_path = _path
            cmde = 'ffmpeg -i ' + downfilm + ' -c copy ' + storage_path + '/' + str(i) + '.mp4'
            os.system(cmde)
            i += 1
            # movie_url = get_url(_url, storage_path)
            # download_movie(movie_url, storage_path)
        except Exception as e:
            print e
