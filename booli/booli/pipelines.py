# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from booli.models import db_connect, create_table, Apartment
from scrapy.exceptions import DropItem


class CleanFloorsPipeline(object):
    def process_item(self, item, spider):
        try:
            text = item["floor"]
        except KeyError:
            text = ['0']
        text = [x if x.isdigit() else (".5" if x == "½" else "") for x in text]
        if len(text) == 0:
            text = ['0']
        text = ''.join(text)
        item["floor"] = int(text)
        return item


class SaveApartmentsPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save apartments to the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        apartment = Apartment()
        exist_apartment = session.query(Apartment).filter_by(id=item["id"]).first()
        key_list = [
            "id",
            "type",
            "fee",
            "price",
            "city",
            "street",
            "street_num",
            "district",
            "postal_code",
            "latitude",
            "longitude",
            "square_meters",
            "floor",
            "housing_society",
            "rooms",
            "construction_year"
        ]
        if exist_apartment is not None:  # the current apartment exists
            raise DropItem(f"Duplicate item found: {item['id']}")
            session.close()
        else:
            for key in key_list:
                try:
                    setattr(apartment, key, item[key])
                except KeyError:
                    pass

            try:
                session.add(apartment)
                session.commit()

            except:
                print('rollbakc')
                session.rollback()
                raise

            finally:
                session.close()

        return item
