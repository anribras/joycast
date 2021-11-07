import json
import logging

import scrapy
import re

CATE_INFO = 'https://www.ximalaya.com/revision/category/allCategoryInfo'
CATE_INFO_STORE = 'ximalaya_categories.json'


def parse_cate_from_file(file):
    with open(file, 'w+') as f:
        try:
            return json.load(f)
        except ValueError:
            return None


class XimalayaSpider(scrapy.Spider):
    name = 'ximalaya'
    json_obj = parse_cate_from_file(CATE_INFO_STORE)
    if json_obj is not None:
        cate_lv1 = set(json_obj['cates_lv1'])
        cate_lv2 = set(json_obj['cates_lv2'])
        cate_lv3 = set(json_obj['cates_lv3'])
    else:
        cate_lv1 = set()
        cate_lv2 = set()
        cate_lv3 = set()
    my_category = {
        'channel': [],
        'category_lv1': [],
        'category_lv2': [],
        'category_lv3': [],
    }
    my_author = {}
    my_album = {}

    def __has_cates_info(self):
        return len(self.cate_lv1) and len(self.cate_lv2) and len(self.cate_lv3)

    def start_requests(self):
        if not self.__has_cates_info():
            yield scrapy.Request(CATE_INFO, self.pare_cate_info)
        url = getattr(self, 'url', None)
        yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        self.parse_cate(response, **kwargs)
        self.parse_author(response, **kwargs)
        yield {
            'category_lv1': list(self.my_category['category_lv1']),
            'category_lv2': list(self.my_category['category_lv2']),
            'category_lv3': list(self.my_category['category_lv3']),
            'channel': self.my_category['channel'],
            'author': self.my_author
        }

    def pare_cate_info(self, response):
        """
        :param response:
        """
        # for json dot operation
        info = response.json()
        for lv1 in info['data']:
            self.cate_lv1.add(lv1['name'])
            for lv2 in lv1['categories']:
                self.cate_lv2.add(lv2['displayName'])
                for lv3 in lv2['subcategories']:
                    self.cate_lv3.add(lv3['displayValue'])
        with open(CATE_INFO_STORE, 'w',encoding='utf-8') as f:
            f.write(
                json.dumps(
                    {
                        'cates_lv1': list(self.cate_lv1),
                        'cates_lv2': list(self.cate_lv2),
                        'cates_lv3': list(self.cate_lv3)
                    },
                    ensure_ascii=False
                )
            )

    def parse_cate(self, response, **kwargs):
        tag_titles = response.css('span.xui-tag-text a::attr(title)').getall()
        tag_hrefs = response.css('span.xui-tag-text a::attr(href)').getall()
        for index, href in enumerate(tag_hrefs):
            tag = tag_titles[index]
            if not re.match('/channel/', href):
                if tag in self.cate_lv1:
                    self.my_category['category_lv1'].append(tag)
                elif tag in self.cate_lv2:
                    self.my_category['category_lv2'].append(tag)
                elif tag in self.cate_lv3:
                    self.my_category['category_lv3'].append(tag)
                else:
                    logging.error('Tag parse error!')
            else:
                self.my_category['channel'].append(tag)

    def parse_author(self, response):
        try:
            url = response.css('div.anchor-info-avatar img::attr(src)').get()
            if isinstance(url, str):
                url = 'https:' + url
            self.my_author['url'] = url
            self.my_author['nickname'] = response.css('p.anchor-info-nick a::text').get()
            self.my_author['introduction'] = response.css('p.anchor-intro::text').getall()[1]
        except ValueError:
            logging.error('Avatar error')
