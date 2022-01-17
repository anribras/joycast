# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

import pymysql
from itemadapter import ItemAdapter
import json
import  hashlib

from backend.app import app
from models import db
from models.user import User
import  sqlalchemy


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
                if not self.track_counts:
                    user = User(username=self.author.nickname,
                                password=hashlib.md5(self.author.nickname.encode('utf-8')).hexdigest(),
                                avatar='https:' + self.author.url,
                                intro=self.author.introduction,
                                user_type=2
                                )
                    try:
                        with app.app_context():
                            db.session.add(user)
                            db.session.commit()
                    except sqlalchemy.exc.IntegrityError as e:
                        logging.info('duplicate user  but is ok')
                    finally:
                        pass
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
