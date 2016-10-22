#coding='utf-8'
'''
爬取“一些”知乎用户
多线程
author:you2mu
time:2016.8.13
'''


import time
import re
from queue import Queue
from threading import Thread

import requests
from bs4 import BeautifulSoup


url_queue = Queue()
for i in range(0,2000,10):   #多线程  url放入队列
    url = 'https://www.zhihu.com/node/TopStory2FeedList?'+'params={"offset":%d,"start":"%d"}&method=next'%(i,i-1)
    url_queue.put(url)
users_queue = Queue()


class Zhihu:

    def __init__(self) :
        self.session = requests.Session()
        self.xsrf = None
        self.links = Queue()  #save users links
        self.users = set()
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.zhihu.com",
        "Upgrade-Insecure-Requests": "1"}
        self.session.headers.update(headers)

    def log(self,str) :
        #str = str.encode()
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log = now_time + '\t\t' + str
        with open('log.txt','a',encoding='utf-8') as f:
            f.writelines(log + '\n')
        print(log)

    #common function
    def get_data(self,path) :
        try:
            html = self.session.get(path).text
        except:
            self.log('connect error when get the data')
            exit(1)
        soup = BeautifulSoup(html,'html.parser')
        return soup

    def get_xsrf(self) :
        path = 'https://www.zhihu.com'
        soup = self.get_data(path)
        tag = soup.find("input",{"name":"_xsrf"})
        self.xsrf = tag.attrs['value']

    def login(self) :
        data = {
        '_xsrf': self.xsrf,
        'password':'yl4321',  #parements
        'remember_me':'true',
        'phone_num':'18428300770'}
        try:
            lgiresp = self.session.post('https://www.zhihu.com/login/phone_num',data=data)
        except:
            self.log('can\'t connect server when you log in')
            exit(1)
        lgiresp = lgiresp.json()

        if lgiresp['msg'] =='登录成功':
            self.log('logged in successful')
            return self.session
        else:
            self.log(lgiresp['msg'])
            self.log('you have not logged in successful')
            exit(1)

    def gt(self) :
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
                   "X-Xsrftoken":self.xsrf,
                   "Host":"www.zhihu.com",
                   "Origin":"https://www.zhihu.com/",
                   "Connection":"keep-alive",
                   # "Cookie":self.session
                   }  #设置为全局变量
        time.sleep(4)
        while not url_queue.empty():
            url = url_queue.get()
            html = self.session.post(url,headers = headers)
            try:
                data = html.json()   #返回的为列表
            except:
                self.log('analysize data error')
            msg = data['msg']   #lock
            if msg==None:
            	self.log('scraping over')
            	exit(1)
            for j in range(0,10):  #知乎的xhr更新为10条
                data = msg[j]
                soup = BeautifulSoup(data,'html.parser')
                author_temp = soup.findAll('a',{'class':'author-link'})    #返回的是列表
                # print(author_temp)
                for m in author_temp:
                	# author = author_temp[0]
                    author = 'https://www.zhihu.com'+ m.attrs['href']
                    self.users.add(author)
                    self.log(author)

if __name__ == '__main__' :
    zhihu = Zhihu()
    zhihu.get_xsrf() #step one get xsrf
    zhihu.login()   #step two login
    threads = []
    for i in range(5):
        t = Thread(target=zhihu.gt,args=())
        t.start()
        threads.append(t)
    for thread in threads :
        thread.join()
