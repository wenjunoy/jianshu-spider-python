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
import cookielib

from utils import saveImagesFromUrl, get_content, get_article, get_collection
from config import COOKIE

logger = logging.getLogger(__name__)
BASE_URL = 'http://www.jianshu.com'

class User(object):
    def __init__(self, user_id='81840abcd13b'):
        self.user_id = user_id
        self.homepageUrl = BASE_URL + '/users/' + user_id + '/latest_articles'
        self.top_articles = BASE_URL + '/users/' + user_id + '/top_articles'
        self.dr = re.compile(r'<[^>]+>',re.S) # 用于去除html的标签，得到正文内容
        self.content = get_content(self.homepageUrl)

    def login(self):
        '''添加cookie并重新得到content
        '''
        self.content = get_content(url=self.homepageUrl, cookie=COOKIE)

    def get_notifications(self):
        '''获取用户提醒，需要登入，设置cookie
        '''
        notifications_url = BASE_URL + '/notifications?all=true'
        time_list = []
        for page in range(1,4):
            url = notifications_url + '&page=' + str(page)
            content = get_content(url, cookie=COOKIE)
            soup = BeautifulSoup(content, 'lxml')
            fa_hearts = soup.find('ul', attrs={'class':'unstyled'}).findAll('li')
            for heart in fa_hearts:
                # logger.info(heart.i['class'])
                # 喜欢你的文章 或者 评论
                if 'fa-heart' in heart.i['class']:
                    time = heart.span.string
                    # user_id = heart.findAll('a')[0]['href'].replace('/users/','')
                    # art_id = heart.findAll('a')[1]['href'].replace('/p/','')
                    time_list.append({'time':time, 'token':'heart'})
                    logger.debug('heart:'+time)
                # 关注了你
                if 'fa-check' in heart.i['class']:
                    time = heart.span.string
                    time_list.append({'time':time, 'token':'check'})
                    logger.debug('check:'+time)
                # 关注了你的专题
                if 'fa-rss-square' in heart.i['class']:
                    time = heart.span.string
                    time_list.append({'time':time, 'token':'square'})
                    logger.debug('square:'+time)
                # add something
        return time_list

    def get_favourites_articles(self, max_get = 100000):
        '''获取用户喜欢的文章，需要登入，设置cookie
        '''
        liked_url = BASE_URL + '/favourites?type=notes'
        page = 1
        favourites_list = []
        while True:
            url = liked_url + '&page=' +str(page)
            page +=1
            content = get_content(url, COOKIE)
            page_arts = get_article(content)
            if len(page_arts) == 0 or len(favourites_list) > max_get:
                logger.info('一共获取 %d 篇文章' % len(favourites_list))
                return favourites_list
            favourites_list.extend(page_arts)

    def get_bookmarks_articles(self, max_get = 10000):
        '''获取用户收藏的文章，需要登入，设置cookie
        '''
        mark_url = BASE_URL + '/bookmarks?'
        page = 1
        bookmarks_list = []
        while True:
            url = mark_url + 'page=' +str(page)
            page +=1
            content = get_content(url, COOKIE)
            page_arts = get_article(content)
            if len(page_arts) == 0 or len(bookmarks_list) > max_get:
                logger.info('一共获取 %d 篇文章' % len(bookmarks_list))
                return bookmarks_list
            bookmarks_list.extend(page_arts)


    def get_user_info(self):
        '''获取用户的基本信息 (user_name, user_intro, followees, followers, articles, write_words, likes)
        '''
        if self.content == "FAIL":
            return {}
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

    def get_article_list(self, order_by = 'lastest', get_max = 1000000):
        '''获取用户的文章列表 order_by = {lastest, top}
        '''
        article_list = {}
        page = 1
        order_url = self.top_articles if order_by == 'top' else self.homepageUrl
        while True:
            url = order_url + '?page=' + str(page)
            page += 1
            content = get_content(url)
            soup = BeautifulSoup(content, 'lxml')
            articles = soup.find('ul', attrs={'class':'article-list latest-notes'}).findAll('li')
            # logger.info(len(articles))
            if not articles or len(article_list) >= max_get:
                logger.info(u'一共获取了 %d 篇文章' % len(article_list))
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
        '''获取关注该用户的所有用户ID
        '''
        followers_url = BASE_URL + '/users/' + self.user_id + '/followers'
        followers_list = []
        page = 1
        while True:
            url = followers_url + '?page=' + str(page)
            page+=1
            content = get_content(url=url)
            soup = BeautifulSoup(content, 'lxml')

            followers = soup.find('ul', attrs={'class':'users'}).findAll('li')
            if not followers:
                logger.info('followers user: %d' % len(followers_list))
                return followers_list
            for follower in followers:
                follower_id = follower.h4.a['href'].replace('/users/','')
                followers_list.append(follower_id)
                logger.debug(follower_id)

    def get_following(self):
        '''获取该用户关注的所有用户ID
        '''
        following_url = BASE_URL + '/users/' + self.user_id + '/following'
        following_list = []
        page = 1
        while True:
            url = following_url + '?page=' + str(page)
            page+=1
            content = get_content(url=url)
            soup = BeautifulSoup(content, 'lxml')

            followings = soup.find('ul', attrs={'class':'users'}).findAll('li')
            if not followings:
                logger.info('following user: %d' % len(following_list))
                return following_list
            for following in followings:
                following_id = following.h4.a['href'].replace('/users/','')
                following_list.append(following_id)
                logger.debug(following_id)


class Article(object):
    def __init__(self, article_id = '0126131adfe7'):
        self.article_id = article_id
        self.pageUrl = BASE_URL + '/p/' + article_id
        self.dr = re.compile(r'<[^>]+>',re.S) # 用于去除html的标签，得到正文内容
        self.content = get_content(url=self.pageUrl)
        if self.content == 'FAIL':
            logger.warning(u'此页面打不开或者该文章不存在')

        self.soup = BeautifulSoup(self.content, 'lxml')

    def get_article_text(self, delete_tag = True, delete_wrap = True):
        if self.content == 'FAIL':
            return None
        title = self.soup.find('div', attrs={'class':'article'}).find('h1',attrs={'class':'title'}).string
        logger.info(title)
        text = self.soup.find('div', attrs={'class': 'article'}).find('div', attrs={'class':'show-content'})
        if delete_tag:
            text = self.dr.sub('',str(text))
            if delete_wrap:
                text = text.replace('\n','')
        logger.debug(text)
        return title, text

    def get_base_info(self):
        if self.content == 'FAIL':
            return None
        note = self.soup.find('script', attrs={'data-name':'note'}).string
        note_json = json.loads(note, encoding='GB2312')

        wordage = int(note_json['wordage'])
        views_count = int(note_json['views_count'])
        comments_count = int(note_json['comments_count'])
        likes_count = int(note_json['likes_count'])
        rewards_total_count = int(note_json['rewards_total_count'])

        base_info ={
            'wordage':wordage,
            'views_count':views_count,
            'comments_count':comments_count,
            'likes_count':likes_count,
            'rewards_total_count': rewards_total_count
        }
        return base_info

    def get_all_imageUrl(self, saveImage = True, path = None):
        '''获取文章中的所有图片链接
        saveImage: 是否下载所有的图片
        path: 下载路径
        '''
        if self.content == 'FAIL':
            return
        imagesUrl_list = []
        images = self.soup.findAll('div', attrs={'class':'image-package'})
        logger.info(u'这篇文章一共有 %d 幅图片。' % len(images))
        for img in images:
            img_url = img.img['src']
            # logger.info(img_url)
            imagesUrl_list.append(img_url)

        if saveImage:
            saveImagesFromUrl(imagesUrl_list, self.article_id if path is None else path)
        return imagesUrl_list


class Notebooks(object):
    def __init__(self, notebook_id='4084323'):
        self.notebook_id = notebook_id
        self.notebookUrl = BASE_URL + '/notebooks/' + notebook_id + '/latest'
        self.content = get_content(self.notebookUrl)

    def get_info(self):
        '''获取基本信息（文章数， 关注数）
        '''
        if self.content == 'FAIL':
            return {}
        soup = BeautifulSoup(self.content, 'lxml')
        ul_meta = soup.find('ul', attrs={'class':'meta'}).findAll('a')
        articles_num = int(re.sub("\D", "", ul_meta[0].string.strip()))
        followers_num = int(re.sub("\D", "", ul_meta[1].string.strip()))
        return {'articles_num': articles_num, 'followers_num': followers_num}


    def get_author_id(self):
        '''获取该文集的作者ID
        '''
        if self.content == 'FAIL':
            return None
        soup = BeautifulSoup(self.content, 'lxml')
        author_id = soup.find('div', attrs={'class':'author'}).div.a['href'].replace('/users/', '')
        logger.debug(author_id)
        return author_id

    def get_subscribers(self, max_get = 10000000):
        '''获取所有关注此文集的用户userid
        '''
        subscribers =[]
        page = 1
        while True:
            url = BASE_URL + '/notebooks/' + self.notebook_id + '/subscribers?page=' + str(page)
            page+=1
            content = get_content(url=url)
            soup = BeautifulSoup(content, 'lxml')
            subs = soup.findAll('a', attrs={'class':'avatar'})
            if not subs or len(subscribers) >= max_get:
                logger.info(u'一共有 %d 人关注此文集' % len(subscribers))
                return subscribers
            for sub in subs:
                user_id = sub['href'].replace('/users/', '')
                logger.debug(user_id)
                subscribers.append(user_id)


    def get_article_list(self, order_by = 'latest', max_get = 1000000):
        '''获取该文集的所有文章列表 order_by : {top, latest}
        '''
        page = 1
        articles_list = []
        while True:
            url = BASE_URL + '/notebooks/' + self.notebook_id + '/' + order_by +'?page='+str(page)
            page += 1
            content = get_content(url)
            page_arts = get_article(content)
            if len(page_arts) == 0 or len(articles_list) > max_get:
                logger.info('一共获取 %d 篇文章' % len(articles_list))
                return articles_list
            articles_list.extend(page_arts)


class Collection(object):
    def __init__(self, collection_id = '3sT4qY'):
        self.collection_id = collection_id
        self.collectionUrl = BASE_URL + '/collection/' + collection_id
        self.content = get_content(self.collectionUrl)
        if self.content == 'FAIL':
            logger.warning(u'此页面无法打开，或者此专题不存在')
        self.soup = BeautifulSoup(self.content, 'lxml')

    def get_collection_num_id(self):
        '''获取collection 的数字ID（collection 包括两个ID）
        '''
        num_id = self.soup.find('script', attrs={'data-name':'collection'}).string
        id_json = json.loads(num_id, encoding='GB2312')
        num_id = int(id_json['id'])
        # logger.info(num_id)
        return num_id

    def get_collection_name(self):
        name = self.soup.find('div', attrs={'class':'header'}).find('h3').a.string
        return name

    def get_article_list(self,fout=None, order_by = 'added_at', max_get = 1000000):
        '''获取此专题的文章列表 （包括阅读，点赞，评论，打赏数目）order_by = {'added_at', 'likes_count'}
        '''
        articles_list = []
        page = 1
        num_id = self.get_collection_num_id()
        coll_name = self.get_collection_name()
        logger.info(u'专题：%s' % coll_name)
        while True:
            url = BASE_URL + '/collections/'+str(num_id)+'/notes?order_by=' + order_by + '&page=' + str(page)
            page += 1
            content = get_content(content)
            page_arts = get_article(content)

            for page_art in page_arts:
                art = Article(page_art['id'])
                title, text = art.get_article_text(delete_wrap =True)
                fout.write(text+'\n')

            if len(page_arts) == 0 or len(articles_list) > max_get:
                logger.info(u'专题 %s 一共获取 %d 篇文章' % (coll_name, len(articles_list)) )
                return articles_list
            articles_list.extend(page_arts)
            logger.info(u'已经获取了 %d 篇文章' % len(articles_list))


    def get_authors(self):
        '''获取此专题的作者（管理者）
        '''
        author_list = []
        authors = self.soup.find('p', attrs={'class': 'author'}).findAll('a')
        for author in authors[1:]:
            author_id = author['href'].replace('/users/', '')
            author_list.append(author_id)
            # logger.info(author_id)
        return author_list

    def get_subscribers(self, max_get = 10000000):
        '''获取关注此专题的user id
        '''
        subscribers =[]
        page = 1
        while True:
            url = self.collectionUrl + '/subscribers?page=' + str(page)
            page+=1
            content = get_content(url=url)
            soup = BeautifulSoup(content, 'lxml')
            subs = soup.findAll('a', attrs={'class':'avatar'})
            if not subs or len(subscribers) >= max_get:
                logger.ifo(u'一共有 %d 人关注此专题' % len(subscribers))
                return subscribers
            for sub in subs:
                user_id = sub['href'].replace('/users/', '')
                subscribers.append(user_id)
                # logger.info(user_id)


class Zodiac(object):
    def __init__(self, year = '2015'):
        self.year = year
        self.zodiacUrl = BASE_URL + '/zodiac/' + year

    def get_articles(self):
        '''获取精选的文章id列表
        '''
        content = get_content(self.zodiacUrl)
        if content == 'FAIL':
            return
        article_list = []
        soup = BeautifulSoup(content, 'lxml')
        pages = soup.findAll('div', attrs={'class':'swiper-slide'})
        for page in pages:
            art_id = page['src'].replace('/p/','')
            logger.info(art_id)
            article_list.append(art_id)
        return article_list


class HomePage(object):
    def __init__(self):
        self.collection = BASE_URL + '/collections'

    def get_articles_hot():
        pass

    def get_novel_selection():
        '''http://www.jianshu.com/recommendations/notes?category_id=66&_=1479483058683
        data-category-id:
        66 : 小说精选
        70 : 摄影游记
        68 : 漫画手绘
        67 : 简约作者
        56 : 新上榜
        60 : 日报
        65 : 专题精选
        61 : 有奖活动
        62 : 简书出版
        63 : 简书播客

        data-dimension
        now : 热门
        weekly : 七日热门
        monthly : 三十日热门
        '''
        recom_url = BASE_URL + '/recommendations/notes'

        pass

    def get_articles_7days_hot():
        pass

    def get_articles_30days_hot():
        pass

    def get_collections_hot(self, order_by='score', max_get = 100000):
        '''order_by : {score（热门排序）, likes_count（关注度）}
        return [{id, name}, ...]
        '''
        page = 1
        collection_list= []
        while True:
            url = self.collection + '?order_by='+order_by+ '&page=' +str(page)
            page +=1
            collections = get_collection(url)
            if len(collections) == 0 or len(collection_list) >= max_get:
                logger.info(u'一共获取 %d 个专题' % len(collection_list))
                return collection_list
            collection_list.extend(collections)
        return collection_list

    def get_collections_recommend(self, order_by = 'newly_added_at', max_get=100000):
        '''order_by = {newly_added_at （最新更新）, score（热门排序）, likes_count（关注度）}
        return [{id, name}, ...]
        '''
        collection_list= []
        page = 1
        while True:
            url = self.collection + '?category_id=58' +'&order_by='+order_by +'&page=' +str(page)
            page+=1
            collections = get_collection(url)
            if len(collections) == 0 or len(collection_list) >= max_get:
                logger.info(u'一共获取 %d 个推荐专题' % len(collection_list))
                return collection_list
            collection_list.extend(collections)
        return collection_list

    def get_collections_city(self, order_by = 'newly_added_at', max_get=100000):
        '''order_by = {newly_added_at（最新更新）, likes_count（关注度）}
        return [{id, name}, ...]
        '''
        collection_list= []
        page = 1
        while True:
            url = self.collection + '?category_id=69' +'&order_by='+order_by +'&page=' +str(page)
            page+=1
            collections = get_collection(url)
            if len(collections) == 0 or len(collection_list) >= max_get:
                logger.info(u'一共获取 %d 城市个专题' % len(collection_list))
                return collection_list
            collection_list.extend(collections)
        return collection_list

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    logging.info("running %s" % " ".join(sys.argv))
    # art = Article()
    # # art.get_article_text()
    # art.get_base_info()

    user = User()
    # user.Login('http://www.jianshu.com/favourites')
    user.get_notifications()
    # user.get_favourites_articles()
    user.get_bookmarks_articles()
    # user.get_following()

    # collection = Collection('1b6650d03fbd')
    # collection.get_article_list()

    # note = Notebooks(notebook_id='1262589')
    # note.get_author_id()
    # logger.info('hahaha')

    # home = HomePage()
    # home.get_collections_hot()
    # home.get_collections_recommend()
    # home.get_collections_city()

    # zo = Zodiac()
    # zo.get_articles()


    pass
