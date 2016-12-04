# -*- coding: utf-8 -*-
''' 参考：http://www.jianshu.com/p/ccab183c50fd
本代码需要先设置cookie: config.py
'''


import matplotlib.pyplot as plt
import json
from collections import defaultdict
import datetime

like = defaultdict(int) # 生成整型默认字典，即字典键的默认值为0
focus = defaultdict(int)
article = defaultdict(int)

from jianshu import User

user = User()
data = user.get_notifications()

for i in data:
    time = i['time'].split(' ')[0]
    if i['token'] == 'heart':
        like[time] += 1
    elif i['token'] == 'check':
        focus[time] += 1
    elif i['token'] == 'square':
        article[time] += 1


for i,c in zip([like, focus, article], ['b-', 'r--', 'go']):
    i = sorted(i.items(), key = lambda x : x[0])
    print i
    x = [datetime.datetime.strptime(j[0],'%Y-%m-%d') for j in i]
    y = [j[1] for j in i]
    plt.plot_date(x, y, c)

plt.savefig('1.jpg',dpi=600)
plt.show()
