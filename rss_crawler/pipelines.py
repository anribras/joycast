# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

import pymysql
from itemadapter import ItemAdapter
import json
import hashlib

from backend.app import app
from models import db, get_one_or_create
from models.v1 import *
import sqlalchemy
from datetime import datetime
import requests


class RssCrawlerPipeline:
    track_counts = 0
    album = None
    author = None
    category = None

    def _process_output_json_file(self, item, spider):
        # Store cates into file
        type_name = type(item).__name__
        if type_name == 'TargetAlbums' and spider.name == 'xima_targets' \
                and len(item.xima) == spider.target_cates_len:
            dir = spider.settings.get('JSONS_DIR')
            file = spider.settings.get('ALBUM_TARGETS_STORE')
            with open(dir + '/' + file, 'w', encoding='utf-8') as f:
                f.write(
                    json.dumps(item.xima, ensure_ascii=False)
                )
        if type_name == 'XimaCatesItem':
            dir = spider.settings.get('JSONS_DIR')
            file = spider.settings.get('CATE_INFO_STORE')
            with open(dir + '/' + file, 'w', encoding='utf-8') as f:
                f.write(
                    json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False)
                )
        if type_name == 'CategoryItem':
            self.category = item
        if type_name == 'AuthorItem':
            self.author = item
        if type_name == 'AlbumItem':
            self.album = item
        if type_name == 'TracksItem':
            if not self.track_counts:
                self.track_counts = len(item.xima)
                self.track_counts -= 1
            else:
                self.track_counts -= 1
                if not self.track_counts:
                    dir = spider.settings.get('JSONS_DIR')
                    file = spider.settings.get('ALBUM_INFO_STORE')
                    album_id = self.album.xima.detail['albumId']
                    with open(dir + '/' + str(album_id) + '_' + file, 'w', encoding='utf-8') as f:
                        f.write(
                            json.dumps({
                                'author': ItemAdapter(self.author).asdict(),
                                'album': ItemAdapter(self.album).asdict(),
                                'category': ItemAdapter(self.category).asdict(),
                                'tracks': item.xima
                            }, ensure_ascii=False)
                        )
        return item

    def _process_output_db(self, item, spider):
        # Store cates into file
        type_name = type(item).__name__
        if type_name == 'CategoryItem':
            self.category = item
        if type_name == 'AuthorItem':
            self.author = item
        if type_name == 'AlbumItem':
            self.album = item
        if type_name == 'TracksItem':
            if not self.track_counts:
                self.track_counts = len(item.xima)
                self.track_counts -= 1
            else:
                self.track_counts -= 1
                # max we crawl 100 tracks for 1 album.
                if not self.track_counts:
                    cate_name = self.category.category_lv2[0]['name']
                    detail = self.album.xima.detail
                    detail_info = detail['albumPageMainInfo']
                    rss_url = 'https://www.ximalaya.com/album/' + str(detail['albumId']) + '.xml'
                    resp = requests.get(rss_url)
                    rss_result = rss_url if resp.text is not None else ''
                    with app.app_context():

                        user, exists = get_one_or_create(db.session, User,
                                                         username=self.author.nickname,
                                                         password=hashlib.md5(
                                                             self.author.nickname.encode('utf-8')).hexdigest(),
                                                         avatar=self.author.url,
                                                         intro=self.author.introduction,
                                                         user_type=2
                                                         )
                        if exists:
                            db.session.add(user)
                            db.session.commit()

                        category, exists = get_one_or_create(db.session, Category, name=cate_name)
                        if exists:
                            db.session.add(category)
                            db.session.commit()

                        album, album_exists = get_one_or_create(db.session, Album,
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
                                                                track_total_counts=len(item.xima),
                                                                category_name=cate_name,
                                                                category_id=category.id,
                                                                user_id=user.id,

                                                                )
                        if exists:
                            db.session.add(album)
                            db.session.commit()

                        statics, exists = get_one_or_create(db.session, AlbumStatics,
                                                            play_counts=detail_info['playCount'],
                                                            subscribe_counts=detail_info['subscribeCount'],
                                                            album_id=album.id,
                                                            vip_type=detail_info['vipType'],
                                                            is_finished=detail_info['isFinished'],
                                                            is_paid=detail_info['isPaid'],
                                                            is_public=detail_info['isPublic'],
                                                            has_buy=detail_info['hasBuy'],
                                                            )
                        if exists:
                            db.session.add(statics)
                            db.session.commit()

                        for ch in [*self.category.channel, *detail_info['tags']]:
                            tag, exists = get_one_or_create(db.session, Tag, name=ch, is_channel=True)
                            if exists:
                                db.session.add(tag)
                                db.session.commit()
                            temp, exists = get_one_or_create(db.session, AlbumTagPivot, album_id=album.id,
                                                             tag_id=tag.id)
                            if exists:
                                db.session.add(temp)
                                db.session.commit()
                        for t in item.xima:
                            info = t['detail']['trackInfo']
                            audio = t['audio']
                            track, exists = get_one_or_create(db.session, Track,
                                                              source_type=0,
                                                              source_id=info['trackId'],
                                                              index=t['index'],
                                                              title=info['title'],
                                                              cover=info['coverPath'],
                                                              rich_intro=info['richIntro'] if 'richIntro' in info else '',
                                                              short_intro=info['shortIntro'] if 'shortIntro' in info else '',
                                                              last_update=datetime.strptime(info['lastUpdate'],"%Y-%m-%d %H:%M:%S"),
                                                              audio=audio['src'] if 'src' in  audio else '',
                                                              audio_duration=audio['sampleDuration'],
                                                              album_id=album.id,
                                                              user_id=user.id)
                            if exists:
                                db.session.add(track)
                                db.session.commit()
                            statics, exists = get_one_or_create(db.session, TrackStatics,
                                                                play_counts=info['playCount'],
                                                                like_counts=info['likeCount'],
                                                                comment_counts=info['commentCount'],
                                                                track_id=track.id)
                            if exists:
                                db.session.add(statics)
                                db.session.commit()
                    # dir = spider.settings.get('JSONS_DIR')
                    # file = spider.settings.get('ALBUM_INFO_STORE')
                    # album_id = self.album.xima.detail['albumId']
                    # with open(dir + '/' + str(album_id) + '_' + file, 'w', encoding='utf-8') as f:
                    #     f.write(
                    #         json.dumps({
                    #             'author': ItemAdapter(self.author).asdict(),
                    #             'album': ItemAdapter(self.album).asdict(),
                    #             'category': ItemAdapter(self.category).asdict(),
                    #             'tracks': item.xima
                    #         }, ensure_ascii=False)
                    #     )

        return item

    def process_item(self, item, spider):
        # return self._process_output_json_file(item, spider)
        return self._process_output_db(item, spider)
