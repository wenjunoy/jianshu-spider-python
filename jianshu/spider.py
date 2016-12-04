#coding: utf-8

from jianshu import User, Article, Notebooks, Collection, HomePage, Zodiac
import logging
import sys

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s',
            level=logging.INFO)
    logging.info("running %s" % " ".join(sys.argv))

    home = HomePage()
    collections = []
    # collections.extend(home.get_collections_hot())
    collections.extend(home.get_collections_recommend())
    # collections.extend(home.get_collections_city())
    # collections = list(set(collections))
    logger.info(u'一共 %d 个专题' % len(collections))
    articles_list = []
    fout = open('jianshu.txt', 'w')
    for collection in collections:
        coll = Collection()
        fout = open(collection['id'], 'w')
        art_list = coll.get_article_list(fout=fout)
        logger.info(u'%s 专题获取了 %d 篇文章' % (collection['name'], len(art_list)))
        articles_list.extend(art_list)
        if len(articles_list) >=500000:
            break


    # articles_list = list(set(articles_list))
    # for i,art_id in enumerate(articles_list):
    #     art =  Article(art_id['id'])
    #     title, text = art.get_article_text()
    #     # logger.info(title)
    #     if i % 10 ==0:
    #         logger.info('已经获取到 %d 篇文章' % i)
