import json
import logging

import scrapy
import re

from xima_crawler.items import *
from xima_crawler.settings import *

import hashlib

from backend.app import app
from models import db, get_one_or_create, update_or_create
from models.v1 import *
import sqlalchemy
from datetime import datetime
import requests


def parse_cate_from_file(file):
    with open(file, 'r') as f:
        try:
            return json.load(f)
        except ValueError:
            return None


class XimalayaSpider(scrapy.Spider):
    download_timeout = 10
    name = 'xima_album_new'
    cate_lv1 = None
    cate_lv2 = None
    cate_lv3 = None
    album_id = 0
    url = ''

    my_category = CategoryItem()
    my_tracks = TracksItem(xima=[])
    my_album = AlbumItem(xima=XimaAlbum())

    user_id = None
    category_id = None
    cate_name = None
    album_id = None
    track_id = None

    def save_cate(self, item: CategoryItem):
        with app.app_context():
            self.cate_name = item.category_lv2[0]['name']
            category, exists = update_or_create(db.session, Category, name=self.cate_name)
            self.category_id = category.id
            db.session.commit()

    def save_user(self, item: AuthorItem):
        with app.app_context():
            user, exists = update_or_create(db.session, User,
                                            is_existed_keys=['username'],
                                            username=item.nickname,
                                            password=hashlib.md5(
                                                item.nickname.encode('utf-8')).hexdigest(),
                                            avatar=item.url,
                                            intro=item.introduction,
                                            user_type=2
                                            )
            self.user_id = user.id
            db.session.commit()

    def save_album(self, item: AlbumItem, track_counts):
        with app.app_context():
            detail = item.xima.detail
            detail_info = detail['albumPageMainInfo']
            rss_url = 'https://www.ximalaya.com/album/' + str(detail['albumId']) + '.xml'
            resp = requests.get(rss_url)
            rss_result = rss_url if len(resp.text) != 0 else ''
            album, exists = update_or_create(db.session, Album,
                                             is_existed_keys=['source_id', 'title'],
                                             source_type=0,
                                             source_id=detail['albumId'],
                                             album_create_date=datetime.strptime(
                                                 detail_info['createDate'], '%Y-%m-%d'),
                                             album_update_date=datetime.strptime(
                                                 detail_info['updateDate'], '%Y-%m-%d'),
                                             title=detail_info['albumTitle'],
                                             short_intro=detail_info['shortIntro'],
                                             rich_intro=detail_info['richIntro'],
                                             rich_detail_intro=detail_info['detailRichIntro'],
                                             cover='https:' + detail_info['cover'],
                                             rss=rss_result,
                                             track_total_counts=track_counts,
                                             category_name=self.cate_name,
                                             category_id=self.category_id,
                                             user_id=self.user_id,
                                             )
            self.album_id = album.id
            statics, exists = update_or_create(db.session, AlbumStatics,
                                               is_existed_keys=['album_id'],
                                               play_counts=detail_info['playCount'],
                                               subscribe_counts=detail_info['subscribeCount'],
                                               album_id=self.album_id,
                                               vip_type=detail_info['vipType'],
                                               is_finished=detail_info['isFinished'],
                                               is_paid=detail_info['isPaid'],
                                               is_public=detail_info['isPublic'],
                                               has_buy=detail_info['hasBuy'],
                                               )

            for ch in [*self.my_category.channel, *detail_info['tags']]:
                tag, exists = update_or_create(db.session, Tag, name=ch, is_channel=True)
                temp, exists = update_or_create(db.session, AlbumTagPivot, album_id=self.album_id, tag_id=tag.id)
            db.session.commit()
            pass

    def save_track(self, item: TracksItem):
        with app.app_context():
            info = item['detail']['trackInfo']
            audio = item['audio']
            logging.info('audio url=' + audio['src'] if 'src' in audio else '')
            track, exists = update_or_create(db.session, Track,
                                             is_existed_keys=['source_id', 'title'],
                                             source_type=0,
                                             source_id=info['trackId'],
                                             index=item['index'],
                                             title=info['title'],
                                             cover=info['coverPath'],
                                             rich_intro=info['richIntro'] if 'richIntro' in info else '',
                                             short_intro=info['shortIntro'] if 'shortIntro' in info else '',
                                             last_update=datetime.strptime(info['lastUpdate'],
                                                                           "%Y-%m-%d %H:%M:%S"),
                                             audio=audio['src'] if 'src' in audio else '',
                                             audio_duration=audio['sampleDuration'],
                                             album_id=self.album_id,
                                             user_id=self.user_id)
            self.track_id = track.id
            statics, exists = update_or_create(db.session, TrackStatics,
                                               is_existed_keys=['track_id'],
                                               play_counts=info['playCount'],
                                               like_counts=info['likeCount'],
                                               comment_counts=info['commentCount'],
                                               track_id=self.track_id)
            logging.info('index=' + str(item['index']))
            db.session.commit()

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

    def parse_tracks(self, response, **kwargs):
        track_page_nums = response.css('ul.pagination-page li:nth-last-child(2) span::text').get()
        # at least search for 1 page
        if track_page_nums is None:
            track_page_nums = 1
        # Max 200 most recent tracks for 1 album
        # Page default size: 50
        if int(track_page_nums) > 4:
            track_page_nums = 4
        track_list_urls = [
            TRACK_LIST + 'albumId=' + self.album_id + '&pageNum=' + str(index) + '&pageSize=50'
            for index in range(1, int(track_page_nums) + 1)
        ]
        yield from response.follow_all(track_list_urls, callback=self.parse_track_list)

    def parse_cate(self, response):
        tag_titles = response.css('span.xui-tag-text a::attr(title)').getall()
        tag_hrefs = response.css('span.xui-tag-text a::attr(href)').getall()
        """
        Speed up
        """
        self.my_category = CategoryItem()
        for index, href in enumerate(tag_hrefs):
            tag = tag_titles[index]
            if not re.match('/channel/', href):
                if tag in self.cate_lv1.keys():
                    self.my_category.category_lv1.append({
                        **self.cate_lv1[tag],
                        "name": tag
                    })
                elif tag in self.cate_lv2.keys():
                    self.my_category.category_lv2.append({
                        **self.cate_lv2[tag],
                        "name": tag
                    })
                elif tag in self.cate_lv3.keys():
                    self.my_category.category_lv3.append({
                        **self.cate_lv3[tag],
                        "name": tag
                    })
                else:
                    logging.error('Tag parse error!')
            else:
                self.my_category.channel.append(tag)

        self.save_cate(self.my_category)
        yield response.follow(self.url, self.parse_author, dont_filter=True)

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

        self.save_user(my_author)
        yield response.follow(ALBUM_INFO + 'albumId=' + self.album_id, self.parse_album)
        # yield my_author

    def parse_album(self, response):
        self.my_album.xima.detail = response.json()['data']
        yield response.follow(self.url, self.parse_tracks, dont_filter=True)
        # yield my_album

    def parse_track_list(self, response, **kwargs):
        length = response.json()['data']['trackTotalCount']
        # final get trackcounts here, save album
        self.save_album(self.my_album, length)

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
                              cb_kwargs={"track": kwargs['track']})

    def parse_track_playurl(self, response, **kwargs):
        index = kwargs['track']['index'] - 1
        self.my_tracks.xima[index]['audio'] = response.json()['data']
        self.save_track(self.my_tracks.xima[index])

        # yield self.my_tracks
