import os
from scrapy import cmdline
# cmd = "scrapy crawl xima_cates -t jsonlines"
# cmd = "scrapy runspider rss_crawler/spiders/xima_albums.py -a url=https://www.ximalaya.com/yinyue/5571971/"
# cmd = "scrapy crawl xima_album -a url=https://www.ximalaya.com/yinyue/41400381/"
# cmd = "scrapy crawl xima_album -a url=https://www.ximalaya.com/keji/55254123/"
# cmd = "scrapy crawl xima_album -a url=https://www.ximalaya.com/youshengshu/40211494/"
# cmd = "scrapy crawl xima_targets "
# cmdline.execute(cmd.split())

import json
with open('rss_crawler/jsons/xima_targets.json', 'r') as f:
    j = json.load(f)
    for key in j:
        lists = j[key]
        for l in lists:
            url = 'https://www.ximalaya.com' + l['link']
            cmd = 'scrapy crawl xima_album -a url=' + url
            os.system(cmd)
            # cmdline.execute(cmd.split())
