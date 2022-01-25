import os
from scrapy import cmdline
# cmd = "scrapy crawl xima_cates -t jsonlines"
cmd = "scrapy crawl xima_album_new -a url=https://www.ximalaya.com/yingshi/37763875/"
cmdline.execute(cmd.split())

import json
import re
# with open('xima_crawler/jsons/xima_targets.json', 'r') as f:
#     last_update = '/yingshi/37763875/'
#     go = False
#     j = json.load(f)
#     for key in j:
#         lists = j[key]
#         for l in lists:
#             url = 'https://www.ximalaya.com' + l['link']
#             cmd = 'scrapy crawl xima_album_new -a url=' + url
#             if re.search(last_update, url):
#                 go = True
#             if go:
#                 os.system(cmd)
