import json
import logging

import scrapy
import re

CATE_INFO = 'https://www.ximalaya.com/revision/category/allCategoryInfo'
CATE_INFO_STORE = 'ximalaya_categories.json'
ALBUM_INFO = 'https://www.ximalaya.com/revision/album/v1/simple?albumId='


def parse_cate_from_file(file):
    with open(file, 'w+') as f:
        try:
            return json.load(f)
        except ValueError:
            return None


class XimalayaSpider(scrapy.Spider):
    name = 'ximalaya'
    url = ''
    json_obj = parse_cate_from_file(CATE_INFO_STORE)
    if json_obj is not None:
        cate_lv1 = json_obj['cates_lv1']
        cate_lv2 = json_obj['cates_lv2']
        cate_lv3 = json_obj['cates_lv3']
    else:
        cate_lv1 = {}
        cate_lv2 = {}
        cate_lv3 = {}
    my_category = {
        'channel': [],
        'category_lv1': [],
        'category_lv2': [],
        'category_lv3': [],
    }
    my_author = {}
    my_album = {'xima':{}}
    my_tracks = {'xima':{}}

    def __has_cates_info(self):
        return len(self.cate_lv1) and len(self.cate_lv2) and len(self.cate_lv3)

    def start_requests(self):
        if not self.__has_cates_info():
            yield scrapy.Request(CATE_INFO, self.pare_cate_info)

        self.url = url = getattr(self, 'url', None)
        yield scrapy.Request(url, self.parse)

        self.my_album['xima']['id'] = album_id = url.split('/')[-2]
        yield scrapy.Request(ALBUM_INFO + album_id, self.parse_album)


    def parse(self, response, **kwargs):

        self.parse_cate(response, **kwargs)
        self.parse_author(response, **kwargs)

        track_page_nums = response.css('ul.pagination-page li:nth-last-child(2) span::text').get()
        track_urls = [self.url+'p'+ str(index) for index in range(1,int(track_page_nums)+1)]

        # self.parse_tracks(response, track_urls=track_urls)

        # yield {
        #     'category_lv1': self.my_category['category_lv1'],
        #     'category_lv2': self.my_category['category_lv2'],
        #     'category_lv3': self.my_category['category_lv3'],
        #     'channel': self.my_category['channel'],
        #     'author': self.my_author,
        #     'album': self.my_album
        # }

    def pare_cate_info(self, response):
        """
        :param response:
        """
        # for json dot operation
        info = response.json()
        for lv1 in info['data']:
            self.cate_lv1[lv1['name']] = {}
            for lv2 in lv1['categories']:
                self.cate_lv2[lv2['displayName']] = {
                    "pinyin": lv2['pinyin'],
                    "link": lv2['link']
                }
                for lv3 in lv2['subcategories']:
                    self.cate_lv3[lv3['displayValue']] = {
                        "pinyin": lv3['code'],
                        "link": lv3['link'],
                    }
        with open(CATE_INFO_STORE, 'w', encoding='utf-8') as f:
            f.write(
                json.dumps(
                    {
                        'cates_lv1': self.cate_lv1,
                        'cates_lv2': self.cate_lv2,
                        'cates_lv3': self.cate_lv3
                    },
                    ensure_ascii=False
                )
            )

    def parse_cate(self, response, **kwargs):
        tag_titles = response.css('span.xui-tag-text a::attr(title)').getall()
        tag_hrefs = response.css('span.xui-tag-text a::attr(href)').getall()
        """
        Speed up
        """
        for index, href in enumerate(tag_hrefs):
            tag = tag_titles[index]
            if not re.match('/channel/', href):
                if tag in self.cate_lv1.keys():
                    self.my_category['category_lv1'].append({
                        **self.cate_lv1[tag],
                        "name": tag
                    })
                elif tag in self.cate_lv2.keys():
                    self.my_category['category_lv2'].append({
                        **self.cate_lv2[tag],
                        "name": tag
                    })
                elif tag in self.cate_lv3.keys():
                    self.my_category['category_lv3'].append({
                        **self.cate_lv3[tag],
                        "name": tag
                    })
                else:
                    logging.error('Tag parse error!')
            else:
                self.my_category['channel'].append(tag)
        yield {
            'category_lv1': self.my_category['category_lv1'],
            'category_lv2': self.my_category['category_lv2'],
            'category_lv3': self.my_category['category_lv3'],
            'channel': self.my_category['channel'],
        }

    def parse_author(self, response):
        try:
            url = response.css('div.anchor-info-avatar img::attr(src)').get()
            if isinstance(url, str):
                url = 'https:' + url
            self.my_author['url'] = url
            self.my_author['nickname'] = response.css('p.anchor-info-nick a::text').get()
            self.my_author['introduction'] = response.css('p.anchor-intro::text').getall()[1]
            yield {
                'author': self.my_author,
            }
        except ValueError:
            logging.error('Avatar error')

    def parse_album(self, response):
        self.my_album['xima']['info'] = response.json()
        yield {
            'album': self.my_album
         }

    def parse_tracks(self, response, **kwargs):
        pass
