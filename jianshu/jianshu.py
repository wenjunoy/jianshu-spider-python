#coding:utf-8
'''
简书爬虫
http://www.jianshu.com
'''

from bs4 import BeautifulSoup
import urllib2
import json
import re, os
import time
import logging
import sys
import requests
from requests.adapters import HTTPAdapter
import cookielib

logger = logging.getLogger("jianshu")
BASE_URL = 'http://www.jianshu.com'


def get_content(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
        'Host' : 'www.jianshu.com',
    }
    # logger.info(headers)
    req = urllib2.Request(url = url, headers = headers)
    try:
        page = urllib2.urlopen(req, timeout = 15)
        content = page.read()
        # logger.info(self.content)
    except Exception,e:
        logger.info("Error: " + str(e) + " URL: " + url)
        content = 'FAIL'
    return content

class User():
    def __init__(self, user_id='81840abcd13b'):
        self.user_id = user_id
        self.homepageUrl = BASE_URL + '/users/' + user_id + '/latest_articles'
        self.top_articles = BASE_URL + '/users/' + user_id + '/top_articles'
        self.dr = re.compile(r'<[^>]+>',re.S) # 用于去除html的标签，得到正文内容
        self.content = self.get_content(self.homepageUrl)

    def get_content(self, url):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
            'Host' : 'www.jianshu.com',
        }
        # logger.info(headers)
        req = urllib2.Request(url = url, headers = headers)
        try:
            page = urllib2.urlopen(req, timeout = 15)
            content = page.read()
            # logger.info(self.content)
        except Exception,e:
            print "Error: " + str(e) + " URL: " + url
            content = 'FAIL'
        return content

    def get_user_info(self):
        if self.content == "FAIL":
            return

        soup = BeautifulSoup(self.content, 'lxml')
        basic_info = soup.find('div', attrs={'class':'basic-info'})
        user_name = basic_info.find('h3').a.string
        user_intro = basic_info.find('p', attrs={'class':'intro'}).string

        clearfix = soup.find('ul', attrs={'class':'clearfix'}).findAll('li')

        followees = int(clearfix[0].a.b.string)
        followers = int(clearfix[1].a.b.string)
        articles = int(clearfix[2].a.b.string)
        write_words = int(clearfix[3].a.b.string)
        likes = int(clearfix[4].a.b.string)
        self.info = {
            'user_name': user_name,
            'user_intro': user_intro,
            'followees': followees,
            'followers': followers,
            'articles': articles,
            'write_words': write_words,
            'likes': likes
        }
        return self.info

    def get_article_list(self):
        article_list = {}
        page = 1
        while True:
            url = self.homepageUrl + '?page=' + str(page)
            page += 1
            content = self.get_content(url)
            soup = BeautifulSoup(content, 'lxml')
            articles = soup.find('ul', attrs={'class':'article-list latest-notes'}).findAll('li')
            # logger.info(len(articles))
            if not articles:
                return article_list
            for art in articles:
                art_id = art.h4.a['href'].replace('/p/', '')
                title = art.h4.a.string
                logger.debug(art_id)
                logger.debug(title)
                if not article_list.has_key(art_link):
                    article_list[art_link] = title
        return article_links

    def get_followers(self):
        followers_url = BASE_URL + '/users/' + self.user_id + '/followers'
        followers_list = []
        page = 1
        while True:
            url = followers_url + '?page=' + str(page)
            page+=1
            content = self.get_content(url=url)
            soup = BeautifulSoup(content, 'lxml')

            followers = soup.find('ul', attrs={'class':'users'}).findAll('li')
            if not followers:
                logger.info('followers user: %d' % len(followers_list))
                return followers_list
            for follower in followers:
                follower_id = follower.h4.a['href'].replace('/users/','')
                followers_list.append(follower_id)
                logger.info(follower_id)

    def get_following(self):
        following_url = BASE_URL + '/users/' + self.user_id + '/following'
        following_list = []
        page = 1
        while True:
            url = following_url + '?page=' + str(page)
            page+=1
            content = self.get_content(url=url)
            soup = BeautifulSoup(content, 'lxml')

            followings = soup.find('ul', attrs={'class':'users'}).findAll('li')
            if not followings:
                logger.info('following user: %d' % len(following_list))
                return following_list
            for following in followings:
                following_id = following.h4.a['href'].replace('/users/','')
                following_list.append(following_id)
                logger.info(following_id)

class Article():
    def __init__(self, article_id = '22998509f00c'):
        self.article_id = article_id
        self.pageUrl = BASE_URL + '/p/' + article_id
        self.dr = re.compile(r'<[^>]+>',re.S) # 用于去除html的标签，得到正文内容
        self.get_content()

    def get_content(self):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
            'Host' : 'www.jianshu.com',
        }
        logger.info(headers)
        req = urllib2.Request(url = self.pageUrl,headers = headers)
        try:
            page = urllib2.urlopen(req,timeout = 15)
            # headers = page.info()
            self.content = page.read()
            # logger.info(content)
        except Exception,e:
            print "Error: " + str(e) + " URL: " + self.pageUrl
            self.content = 'FAIL'
            return "FAIL"
        return self.content

    def get_article_text(self, delete_tag = True, delete_wrap = True):
        if self.content == 'FAIL':
            return None
        soup = BeautifulSoup(self.content, 'lxml')
        # info = soup.find('div', attrs={'class':'meta-top'})
        # wordage = info.find('span', attrs={'class':'wordage'})
        # view_count = info.find('span', attrs={'class':'view-count'})
        # comment_count = info.find('span', attrs={'class':'comment-count'})
        # likes_count = info.find('span', attrs={'class':'likes-count'})
        # logger.info(likes_count)

        title = soup.find('div', attrs={'class':'article'}).find('h1',attrs={'class':'title'}).string
        logger.info(title)
        text = soup.find('div', attrs={'class': 'article'}).find('div', attrs={'class':'show-content'})
        if delete_tag:
            text = self.dr.sub('',str(text))
            if delete_wrap:
                text = text.replace('\n','')

        logger.info(text)
        return title, text

    def get_all_imageUrl(self):
        #TODO
        pass



def get_article(url):
    '''获取文章的通用函数
    '''
    articles_list = []
    content = get_content(url)
    soup = BeautifulSoup(content, 'lxml')
    if content == 'FAIL':
        return articles_list
    arts = soup.findAll('h4', attrs={'class':'title'})
    footers = soup.findAll('div', attrs={'class':'list-footer'})

    if not arts or not footers:
        return articles_list
    for art, footer in zip(arts, footers):
        # logger.info(art)
        art_id = art.a['href'].replace('/p/','')
        logger.info(art.a.string)

        a_list = footer.findAll('a')
        views_count = int(re.sub("\D", "", a_list[0].string.strip()))
        comments_count = int(re.sub("\D", "", a_list[1].string.strip()))
        span_list = footer.findAll('span')
        likes_count = int(re.sub("\D", "", span_list[0].string.strip()))
        if len(span_list) < 2:
            rewards_count = 0
        else:
            rewards_count = int(re.sub("\D", "", span_list[1].string.strip()))
        articles_list.append({'id':art_id, 'views':views_count, 'comments':comments_count, 'likes':likes_count, 'rewards':rewards_count})
    return articles_list

class Notebooks():
    def __init__(self, notebook_id='4084323'):
        self.notebook_id = notebook_id
        self.notebookUrl = BASE_URL + '/notebooks/' + notebook_id + '/latest'
        self.content = get_content(self.notebookUrl)

    def get_article_list(self, order_by = 'top', max_get = 1000000):
        page = 1
        articles_list = []
        while True:
            url = BASE_URL + '/notebooks/' + self.notebook_id + '/' + order_by +'?page='+str(page)
            page += 1
            page_arts = get_article(url)
            if len(page_arts) == 0 or len(articles_list) > max_get:
                logger.info('一共获取 %d 篇文章' % len(articles_list))
                return articles_list
            articles_list.extend(page_arts)


class Collection():
    def __init__(self, collection_id = '3sT4qY'):
        self.collection_id = collection_id
        self.collectionUrl = BASE_URL + '/collection/' + collection_id

        self.content = get_content(self.collectionUrl)

    def get_collection_num_id(self):
        '''获取collection 的数字ID（collection 包括两个ID）
        '''
        if self.content == 'FAIL':
            return
        soup = BeautifulSoup(self.content, 'lxml')
        num_id = soup.find('script', attrs={'data-name':'collection'}).string
        id_json = json.loads(str(num_id))
        num_id = int(id_json['id'])
        # logger.info(num_id)
        return num_id


    def get_collection_content(self, url):
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36",
            'Host' : 'www.jianshu.com',
            'Referer': self.collectionUrl
        }
        req = urllib2.Request(url = url, headers = headers)
        try:
            page = urllib2.urlopen(req, timeout = 15)
            content = page.read()
            # logger.info(self.content)
        except Exception,e:
            logger.info("Error: " + str(e) + " URL: " + url)
            content = 'FAIL'
        return content

    # order_by = {'added_at', 'likes_count'}
    def get_article_list(self, order_by = 'likes_count', max_get = 1000000):
        '''获取此专题的文章列表 （包括阅读，点赞，评论，打赏数目）
        '''
        articles_list = []
        page = 1
        num_id = self.get_collection_num_id()
        while True:
            url = BASE_URL + '/collections/'+str(num_id)+'/notes?order_by=' + order_by + '&page=' + str(page)
            page += 1
            page_arts = get_article(url)
            if len(page_arts) == 0 or len(articles_list) > max_get:
                logger.info('一共获取 %d 篇文章' % len(articles_list))
                return articles_list
            articles_list.extend(page_arts)


    def get_authors(self):
        '''获取此专题的作者（管理者）
        '''
        if self.content == 'FAIL':
            return
        author_list = []
        soup = BeautifulSoup(self.content, 'lxml')
        authors = soup.find('p', attrs={'class': 'author'}).findAll('a')
        for author in authors[1:]:
            author_id = author['href'].replace('/users/', '')
            author_list.append(author_id)
            # logger.info(author_id)
        return author_list

    def get_subscribers(self):
        '''获取关注此专题的user id
        '''
        subscribers =[]
        page = 1
        while True:
            url = self.collectionUrl + '/subscribers?page=' + str(page)
            page+=1
            content = self.get_content(url=url)
            soup = BeautifulSoup(content, 'lxml')
            subs = soup.findAll('a', attrs={'class':'avatar'})
            if not subs:
                return subscribers
            for sub in subs:
                user_id = sub['href'].replace('/users/', '')
                subscribers.append(user_id)
                # logger.info(user_id)


class HomePage():
    def __init__(self):
        self.collection = BASE_URL + '/collections'

    def get_collection_list(self, max_get = 30):
        page = 1
        collection_list= []
        while True:
            url = self.collection + '?page=' +str(page)
            content = get_content(url)
            soup = BeautifulSoup(content, 'lxml')
            collections = soup.findAll('a', attrs={'class':'avatar'})
            if not collections:
                logger.info('一共获取 %d 个专题' % len(collection_list))
                return collection_list
            for coll in collections:
                coll_id = coll['href'].replace('/collection/', '')
                logger.info(coll_id)
                collection_list.append(coll_id)
                if len(collection_list) >= max_get:
                    logger.info('一共获取 %d 个专题' % len(collection_list))
                    return collection_list

        return collection_list



if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logging.info("running %s" % " ".join(sys.argv))
    # art = Article(article_id = '22998509f00c', user_id='81840abcd13b')
    # art.get_article_text()

    # user = User()
    # user.get_following()
    # collection = Collection('1b6650d03fbd')
    # collection.get_article_list()

    # note = Notebooks(notebook_id='4084323')
    # note.get_article_list()
    # logger.info('hahaha')

    home = HomePage()
    home.get_collection_list()

    pass
