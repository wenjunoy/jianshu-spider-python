# coding:utf-8
import logging
import urllib2
import requests
from bs4 import BeautifulSoup
import sys, os

logger = logging.getLogger(__name__)

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

def saveImagesFromUrl(images, filePath):
    logger.info('sum of the  images: %d ' % len(images))
    if not images:
        logger.info('imagesUrl is empty')
        return
    if not os.path.exists(filePath):
        os.makedirs(filePath)

    nameNumber = 0
    for image in images:
        suffix = '.jpg'
        fileName = filePath +'/'  + str(nameNumber) + suffix
        nameNumber += 1
        try:
            # 设置超时重试次数及超时时间单位秒
            logger.debug('fileName:'+fileName)
            logger.debug('imageurl:'+image)
            response = requests.get(image, timeout=20)
            contents = response.content
            with open(fileName, "wb") as pic:
                pic.write(contents)

        except IOError:
            logger.warning('Io error')
        except requests.exceptions.ConnectionError:
            logger.warning('连接超时,URL: %s' % image)
    logger.info('图片下载完毕')
