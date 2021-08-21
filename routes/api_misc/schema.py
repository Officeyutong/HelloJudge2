from dataclasses import field
from marshmallow_dataclass import dataclass

from typing import List


@dataclass
class HomepageSwiperEntry:
    image_url: str
    link_url: str


@dataclass
class HomepageSwiperList:
    data: List[HomepageSwiperEntry]


homepage_swiper_schema = HomepageSwiperList.Schema()
