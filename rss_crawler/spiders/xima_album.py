import json
import logging

import scrapy
import re

from rss_crawler.items import *
from rss_crawler.settings import *

def parse_cate_from_file(file):
    with open(file, 'r') as f:
        try:
            return json.load(f)
        except ValueError:
            return None

class XimalayaSpider(scrapy.Spider):
    download_timeout = 10
    name = 'xima_album'
    cate_lv1 = None
    cate_lv2 = None
    cate_lv3 = None
    album_id = 0
    url = ''
    my_tracks = TracksItem(xima=[])

    def __has_cates_info(self):
        return len(self.cate_lv1) and len(self.cate_lv2) and len(self.cate_lv3)

    def start_requests(self):
        file = JSONS_DIR + '/' + CATE_INFO_STORE
        cates = parse_cate_from_file(file)
        if cates is not None:
            self.cate_lv1 = cates['lv1']
            self.cate_lv2 = cates['lv2']
            self.cate_lv3 = cates['lv3']
        else:
            raise ValueError
        self.url = getattr(self, 'url', None)
        self.album_id = self.url.split('/')[-2]

        yield scrapy.Request(self.url, self.parse_cate, dont_filter=True)
        yield scrapy.Request(self.url, self.parse_author, dont_filter=True)
        yield scrapy.Request(ALBUM_INFO + 'albumId=' + self.album_id, self.parse_album)
        yield scrapy.Request(self.url, self.parse_tracks, dont_filter=True)

    def parse_tracks(self, response, **kwargs):
        track_page_nums = response.css('ul.pagination-page li:nth-last-child(2) span::text').get()
        # at least search for 1 page
        if track_page_nums is None:
            track_page_nums = 1
        track_list_urls = [
            TRACK_LIST + 'albumId=' + self.album_id + '&pageNum=' + str(index)
            for index in range(1, int(track_page_nums) + 1)
        ]
        yield from response.follow_all(track_list_urls, callback=self.parse_track_list)

    def parse_cate(self, response):
        tag_titles = response.css('span.xui-tag-text a::attr(title)').getall()
        tag_hrefs = response.css('span.xui-tag-text a::attr(href)').getall()
        """
        Speed up
        """
        my_category = CategoryItem()
        for index, href in enumerate(tag_hrefs):
            tag = tag_titles[index]
            if not re.match('/channel/', href):
                if tag in self.cate_lv1.keys():
                    my_category.category_lv1.append({
                        **self.cate_lv1[tag],
                        "name": tag
                    })
                elif tag in self.cate_lv2.keys():
                    my_category.category_lv2.append({
                        **self.cate_lv2[tag],
                        "name": tag
                    })
                elif tag in self.cate_lv3.keys():
                    my_category.category_lv3.append({
                        **self.cate_lv3[tag],
                        "name": tag
                    })
                else:
                    logging.error('Tag parse error!')
            else:
                my_category.channel.append(tag)
        yield my_category

    def parse_author(self, response):
        my_author = AuthorItem()
        try:
            url = response.css('div.anchor-info-avatar img::attr(src)').get()
            if isinstance(url, str):
                url = 'https:' + url
            my_author.url = url
            my_author.nickname = response.css('p.anchor-info-nick a::text').get()
            intro = response.css('p.anchor-intro::text').getall()
            my_author.introduction = intro[1] if len(intro) > 1 else intro[0]
        except ValueError:
            logging.error('Avatar error')
        yield my_author

    def parse_album(self, response):
        my_album = AlbumItem(xima=XimaAlbum())
        my_album.xima.detail = response.json()['data']
        yield my_album

    def parse_track_list(self, response, **kwargs):
        length = response.json()['data']['trackTotalCount']
        if (not len(self.my_tracks.xima)):
            self.my_tracks.xima = [{}] * length
        for track in response.json()['data']['tracks']:
            index = track['index']
            track_id = track['trackId']
            self.my_tracks.xima[index - 1] = track
            yield response.follow(TRACK_INFO + 'trackId=' + str(track_id),
                                  callback=self.parse_track_info,
                                  # pass index to next parser
                                  cb_kwargs={"track": track})

    def parse_track_info(self, response, **kwargs):
        index = kwargs['track']['index'] - 1
        track_id = kwargs['track']['trackId']
        self.my_tracks.xima[index]['detail'] = response.json()['data']
        yield response.follow(TRACK_PLAY_URL + 'id=' + str(track_id),
                              callback=self.parse_track_playurl,
                              # pass index to next parser
                              cb_kwargs={"track":  kwargs['track']})

    def parse_track_playurl(self, response, **kwargs):
        index = kwargs['track']['index'] - 1
        self.my_tracks.xima[index]['audio'] = response.json()['data']
        yield self.my_tracks
