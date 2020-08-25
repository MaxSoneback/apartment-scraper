# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader.processors import MapCompose, TakeFirst, Identity
import re


def split_by_comma(text):
    return [text.split(',')]


def split_by_dot(text):
    return [text.split('.')]


def cast_int(val):
    try:
        return int(val)
    except ValueError:
        return val


def split_string(text):
    return [text.split()]


def return_digits(text):
    text = [x if x.isdigit() else (".5" if x == "½" else "") for x in text]
    if len(text) == 0:
        text = ['0']
    return ''.join(text)


def take_first(arr):
    return arr[0]


def take_second(arr):
    return arr[1]


def take_third(arr):
    return arr[2]


def take_last(arr):
    return arr[-1]


def remove_last(text):
    return text[:-1]


def take_street(string):
    pattern = '\S*\d+\S*'
    match = re.search(pattern, string)
    if match:
        return match.string[:match.start(0)]
    else:
        return None


def take_num(string):
    pattern = '\S*\d+\S*'
    match = re.search(pattern, string)
    if match:
        return match[0]
    else:
        return None


class AccommodationItem(Item):
    id = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )

    type = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )

    price = Field(
        input_processor=MapCompose(return_digits, cast_int),
        output_processor=TakeFirst()
        )

    city = Field(
        input_processor=MapCompose(str.strip, split_by_dot, take_first, split_string, take_last),
        output_processor=TakeFirst()
    )
    street = Field(
        input_processor=MapCompose(str.strip, split_by_comma, take_first, take_street, str.strip),
        output_processor=TakeFirst()
    )
    street_num = Field(
        input_processor=MapCompose(str.strip, split_by_comma, take_first, take_num),
        output_processor=TakeFirst()
    )
    district = Field(
        input_processor=MapCompose(str.strip, split_by_comma, take_second, str.strip),
        output_processor=TakeFirst()
    )
    rooms = Field(
        input_processor=MapCompose(str.strip, split_by_comma, take_first, return_digits, cast_int),
        output_processor=TakeFirst()
    )
    square_meters = Field(
        input_processor=MapCompose(str.strip, split_by_comma, take_second, return_digits, remove_last, cast_int),
        output_processor=TakeFirst()
    )
    construction_year = Field(
        input_processor=MapCompose(str.strip, cast_int),
        output_processor=TakeFirst()
    )
    postal_code = Field(
        input_processor=MapCompose(return_digits, cast_int),
        output_processor=TakeFirst()
    )
    latitude = Field(
        input_processor=Identity(),
        output_processor=TakeFirst()
    )
    longitude = Field(
        input_processor=Identity(),
        output_processor=TakeFirst()
    )


class ApartmentItem(AccommodationItem):
    fee = Field(
        input_processor=MapCompose(str.strip, return_digits, cast_int),
        output_processor=TakeFirst()
    )
    floor = Field(
        # value = ['BV  '] breaks the code for some reason, implementing pipeline CleanRoomsPipeline to clean this instead
        input_processor=Identity(),
        output_processor=TakeFirst()
    )
    housing_society = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )


class HouseItem(AccommodationItem):
    yard_size = Field(
        output_processor=TakeFirst()
    )
    gross_floor_area = Field(
        output_processor=TakeFirst()
    )
    living_area = Field(
        output_processor=TakeFirst()
    )
    type = Field(
        output_processor=TakeFirst()
    )
    rateable_value = Field(
        output_processor=TakeFirst()
    )