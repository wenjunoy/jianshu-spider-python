#coding: utf-8
import logging
logger =logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s',
        level=logging.DEBUG)

from jianshu.jianshu import User, Article, HomePage, Collection,Notebooks,Zodiac

art = Article('af14524650e2')
art.get_article_text()
art.get_base_info()
art.get_all_imageUrl()

user = User(user_id='81840abcd13b')
user.get_user_info()
user.get_article_list()
user.get_following()
user.get_followers()

user.get_notifications()
user.get_favourites_articles()
user.get_bookmarks_articles()
user.get_subscription_notes()

collection = Collection('1b6650d03fbd')
collection.get_authors()
collection.get_subscribers()
collection.get_article_list()

note = Notebooks(notebook_id='1262589')
note.get_author_id()
note.get_subscribers()
note.get_article_list()

home = HomePage()
home.get_collections_hot()
home.get_collections_recommend()
home.get_collections_city()

zo = Zodiac()
zo.get_articles()
