# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json


class RssCrawlerPipeline:
    track_counts = 0
    album = None
    author = None
    category = None

    def process_item(self, item, spider):
        # Store cates into file
        type_name = type(item).__name__
        if type_name == 'TargetAlbums' and spider.name == 'xima_targets'\
                and len(item.xima) == spider.target_cates_len:
            dir = spider.settings.get('JSONS_DIR')
            file = spider.settings.get('ALBUM_TARGETS_STORE')
            with open(dir + '/' + file, 'w', encoding='utf-8') as f:
                f.write(
                    json.dumps(item.xima, ensure_ascii=False)
                )
        if type_name  == 'XimaCatesItem':
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
