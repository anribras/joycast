# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from dataclasses import dataclass, field

@dataclass
class XimaCatesItem:
    lv1: dict = field(default_factory=dict)
    lv2: dict = field(default_factory=dict)
    lv3: dict = field(default_factory=dict)

@dataclass
class CategoryItem:
    channel: list = field(default_factory=list)
    category_lv1: list = field(default_factory=list)
    category_lv2: list = field(default_factory=list)
    category_lv3: list = field(default_factory=list)


@dataclass
class AuthorItem:
    url: str = ''
    nickname: str = ''
    introduction: str = ''


@dataclass
class XimaAlbum:
    detail: dict = field(default_factory=dict)


@dataclass
class AlbumItem:
    xima: XimaAlbum


@dataclass
class TracksItem:
    xima: list = field(default_factory=list)
