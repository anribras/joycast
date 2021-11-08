import json
import logging

import scrapy
import re

from ..items import *
from ..settings import *


class XimaCatesSpider(scrapy.Spider):
    name = 'xima_cates'

    def start_requests(self):
        yield scrapy.Request(CATE_INFO, self.parse_cate_info)

    def parse_cate_info(self, response):
        """
        :param response:
        """
        cates = XimaCatesItem()
        # for json dot operation
        info = response.json()
        for lv1 in info['data']:
            cates.lv1[lv1['name']] = {}
            for lv2 in lv1['categories']:
                cates.lv2[lv2['displayName']] = {
                    "pinyin": lv2['pinyin'],
                    "link": lv2['link']
                }
                for lv3 in lv2['subcategories']:
                    cates.lv3[lv3['displayValue']] = {
                        "pinyin": lv3['code'],
                        "link": lv3['link'],
                    }
        yield cates

