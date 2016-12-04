# jianshu spider

### 简要介绍

本代码主要是提供一系列的API，用于爬取[简书](https://www.jianshu.com)上的内容。可以抓取简书上用户相关信息，写的文章。还有抓取简书上所有的专题和文集，获取专题和文集的相关信息和所有文章。

不保证代码一直有效（如果简书网站结构和API变化）

### 依赖
```
BeautifulSoup
urllib2
requests
```

### 如何使用

获取代码：
```
git clone git@github.com:wenjunoy/jianshu-spider-python.git
```

#### 获取用户个人信息

url形式： http://www.jianshu.com/users/< ID >/latest_articles
获取user的相关内容，包括基本信息（关注数，粉丝，文章数，字数，获得的喜欢），所有的文章，关注的人，和被关注的人。

```
from jianshu.jianshu import User
user = User(user_id='81840abcd13b')
user.get_user_info() # 获取基本信息
user.get_article_list() # 获取文章列表
user.get_following() # 获取关注的用户
user.get_followers() # 获取被关注的用户
```

通过登入自己的账户还可以获取喜欢的文章id(文章的url是 http://www.jianshu.com/p/< id >)，收藏的文章和关注的专题最新的文章。必需在jianshu/config.py 设置COOKIE。
```
user.get_favourites_articles()
user.get_bookmarks_articles()
user.get_subscription_notes()
```
通过通知页面可以绘制你的 简书文章-关注曲线
```
from jianshu.plot import draw_niti
draw_niti(user_id='81840abcd13b')
```

![关注曲线](http://7xlx99.com1.z0.glb.clouddn.com/jianshu/jianshuquxian.jpg)

*参考[简书作者-treelake](http://www.jianshu.com/users/66f24f2c0f36/latest_articles)的文章[绘制你的简书曲线](http://www.jianshu.com/p/ccab183c50fd)*

#### 获取所有的专题

根据主页的[主题广场](http://www.jianshu.com/collections)可以获取所有的专题ID

![专题广场](http://7xlx99.com1.z0.glb.clouddn.com/jianshu/20161204223235.png)

```
from jianshu.jianshu import HomePage
home = HomePage()
home.get_collections_hot()  # 获取热门专题
home.get_collections_recommend() #获取推荐专题
home.get_collections_city() # 获取城市专题
```
通过参数**order_by*** 和**max_get**的设置获取你想要的专题顺序和数目。

#### 获取专题内容

url形式： http://www.jianshu.com/collection/< ID >
通过专题的ID可以获取该专题的相关内容，包括专题的管理员，关注此专题的用户以及文章列表。
```
from jianshu.jianshu import Collection
collection = Collection('40d81e34a7fb')
collection.get_authors()
collection.get_subscribers()
collection.get_article_list()
```

#### 获取文集内容

url 形式： http://www.jianshu.com/notebooks/< ID >/latest
通过文集的ID可以获取该文集的相关内容，包括基本信息，文集的作者，关注的人和文章列表。

```
from jianshu.jianshu import Notebooks
note = Notebooks('3864458')
note.get_author_id()
note.get_subscribers()
note.get_article_list()
```

#### 获取文章内容

url形式： http://www.jianshu.com/p/< ID >
通过文章的ID和获取文章的相关内容，基本信息（字数，阅读量，评论数和打赏数），文章的内容（可以选择删除网页标签和换行符），还可以下载文章内的所有图片。

```
from jianshu.jianshu import Article
art = Article('af14524650e2')
art.get_base_info() # 基本信息
art.get_article_text() # 文章的内容
art.get_all_imageUrl() # 获取文章的图片并保存
```

#### 获取2015年精选文章
url: http://www.jianshu.com/zodiac/2015
```
zo = Zodiac()
zo.get_articles()
```

该代码只是简书爬虫的一系列的API，爬虫机制还需要自己去完成。目前只支持单线程。
