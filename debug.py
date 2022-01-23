import os
from scrapy import cmdline
# cmd = "scrapy crawl xima_cates -t jsonlines"
# cmd = "scrapy runspider xima_crawler/spiders/xima_albums.py -a url=https://www.ximalaya.com/yinyue/5571971/"
# cmd = "scrapy crawl xima_album -a url=https://www.ximalaya.com/yinyue/41400381/"
# cmd = "scrapy crawl xima_album -a url=https://www.ximalaya.com/yingshi/37763875/"
# cmd = "scrapy crawl xima_album_new -a url=https://www.ximalaya.com/ertong/9031108/"
# cmdline.execute(cmd.split())

import json
import re
with open('xima_crawler/jsons/xima_targets.json', 'r') as f:
    last_update = '/yingshi/35468142/'
    go = True
    j = json.load(f)
    for key in j:
        lists = j[key]
        for l in lists:
            url = 'https://www.ximalaya.com' + l['link']
            cmd = 'scrapy crawl xima_album_new -a url=' + url
            if re.search(last_update, url):
                go = True
            if go:
                os.system(cmd)
