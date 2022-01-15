import json

import scrapy
from ..settings import *
from ..items import *


class XimaTargetsSpider(scrapy.Spider):
    TARGET_CATES = [
        '有声书',
        '段子',
        '情感生活',
        '娱乐',
        '影视',
        '儿童',
        '历史',
        '商业财经',
        'IT科技',
        '个人成长',
        '头条',
        '二次元',
        '旅游',
        '汽车',
        '人文'
    ]
    target_cates_len = len(TARGET_CATES)
    name = 'xima_targets'
    cates = {}
    my_target = TargetAlbums()

    def start_requests(self):
        with open(JSONS_DIR + '/' + CATE_INFO_STORE, 'r') as f:
            self.cates = json.load(f)

        # for c in self.cates['lv2'].keys():
        for c in self.TARGET_CATES:
            url = ALBUM_TARGETS + 'category=' + self.cates['lv2'][c]['pinyin']
            yield scrapy.Request(url, callback=self.parse, meta={'cate': c})

    def parse(self, response, **kwargs):
        cate = response.meta['cate']
        data = response.json()['data']
        albums_list = [{
                'albumId': album['albumId'],
                'link': album['link'],
                'playCount': album['playCount'],
                'trackCount': album['trackCount'],} for album in data['albums']]
        self.my_target.xima[cate] = albums_list
        yield response.follow(ALBUM_RSS_FEED + str())
        yield self.my_target