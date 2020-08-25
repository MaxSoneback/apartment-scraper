import scrapy
import re
from scrapy.loader import ItemLoader
from booli.items import ApartmentItem
import requests
from itertools import zip_longest
from scrapy.utils.log import configure_logging
import logging
from credentials import api_key


class ApartmentSpider(scrapy.Spider):
    name = "apartments"
    api_format = "json"
    api_base = f"https://reverse.geocoder.ls.hereapi.com/6.2/reversegeocode.{api_format}"

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def start_requests(self):
        urls = [
            'https://www.booli.se/uppsala/419/',
            'https://www.booli.se/goteborg/22/',
            'https://www.booli.se/stockholm/1/',
            'https://www.booli.se/malmo/78/',
            'https://www.booli.se/orebro/334/',
            'https://www.booli.se/linkoping/393/',
            'https://www.booli.se/vasteras/424/',
            'https://www.booli.se/helsingborg/88/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def create_link_pos_dict(self, lat, lon, rel_links):
        """
        :param lat: lista med latituder,
        :param lon: lista med longituder,
        :param rel_links: lista med relativa länkar,
        :return: nyckel-värdepar med länkar som nycklar och position som värde, ex "annons/12345": (17.12, 15.45)
        """
        pos = tuple(zip(lat, lon))
        pos_map = dict((link, pos) for link, pos in zip_longest(rel_links, pos))
        return pos_map

    def parse(self, response, city=None):
        if city is None:
            city = response.xpath("//h1[@class='search-summary__text']").get()

        listings = response.xpath("//div[@class='search-list__pagination']"
                                  "/preceding-sibling::ul[1]"
                                  "/li[@class='search-list__item search-list__item--listing']")

        #lat_list = listings.xpath("./a/@data-latitude").getall()
        #lon_list = listings.xpath("./a/@data-longitude").getall()
        #link_list = listings.xpath("./a/@href").getall()
        #link_pos_dict = self.create_link_pos_dict(lat_list, lon_list, link_list)

        # TODO: Gör en batch geocode POST till HERE API för att få alla ZIP-koder till bostäderna på 1 sida

        for listing in listings:
            link = listing.xpath("./a/@href").get()
            pos = (listing.xpath("./a/@data-latitude").get(), listing.xpath("./a/@data-longitude").get())
            if re.search("annons", link) is not None:
                yield response.follow(link, callback=self.parse_listing, cb_kwargs=dict(pos=pos, link=link, city=city))

            elif re.search("bostad", link) is not None:
                yield response.follow(link, callback=self.parse_listing, cb_kwargs=dict(pos=pos, link=link, city=city))

        next_page = response.xpath("//div[@class='search-list__pagination-links']/"
                                   "a[@class='search-list__pagination-link search-list__pagination-link--next']") \
            .xpath('@href').get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse, cb_kwargs=dict(city=city))

    def parse_listing(self, response, pos, link, city):
        loader = ItemLoader(item=ApartmentItem(), response=response)

        zip_response = requests.get(
            self.api_base,
            params={'apiKey': api_key,
                    'mode': "retrieveaddress",
                    'addressattributes': "postalCode",
                    'prox': f"{pos[0]},{pos[1]},0"},
        )
        data = zip_response.json()
        zip = data["Response"]["View"][0]["Result"][0]["Location"]["Address"]["PostalCode"]

        loader.add_value("id", link)
        loader.add_xpath("type", "//li/span[text()='Bostadstyp']/following-sibling::span/text()")
        loader.add_value("city", city)
        loader.add_xpath("street", "//span[@class='property__header__street-address']/text()")
        loader.add_xpath("street_num", "//span[@class='property__header__street-address']/text()")
        loader.add_xpath("district", "//span[@class='property__header__street-address']/text()")
        loader.add_value("postal_code", zip)
        loader.add_value("latitude", float(pos[0]))
        loader.add_value("longitude", float(pos[1]))

        loader.add_xpath("price", "//span[@class='property__base-info__title__price']/text()")
        loader.add_xpath("floor", "//li/span[text()='Våning']/following-sibling::span/text()")
        loader.add_xpath("rooms", "//span[@class='property__base-info__title__size']/text()")
        loader.add_xpath("square_meters", "//span[@class='property__base-info__title__size']/text()")
        loader.add_xpath("construction_year", "//li/span[text()='Byggår']/following-sibling::span/text()")
        loader.add_xpath("fee", "//li/span[text()='Avgift']/following-sibling::span/text()")
        loader.add_xpath("housing_society",
                         "//li/span[text()='Bostadsrättsförening']/following-sibling::span/descendant-or-self::a/text()")
        loader.add_xpath("housing_society",
                         "//li/span[text()='Bostadsrättsförening']/following-sibling::a/text()")

        return loader.load_item()

        # ul_properties = response.xpath("//ul[@class='property__base-info__list']")
        # yield {
        #     "address": response.xpath("//span[@class='property__header__street-address']/text()").get(),
        #     "rum_kvm": response.xpath("//span[@class='property__base-info__title__size']/text()").get(),
        #     "pris": response.xpath("//span[@class='property__base-info__title__price']/text()").get(),
        #     "avgift": ul_properties.xpath("./li/span[text()='Avgift']/following-sibling::span/text()").get(),
        #     "bostadstyp": ul_properties.xpath("./li/span[text()='Bostadstyp']/following-sibling::span/text()").get(),
        #     "vaning": ul_properties.xpath("./li/span[text()='Våning']/following-sibling::span/text()").get(),
        #     "byggar": ul_properties.xpath("./li/span[text()='Byggår']/following-sibling::span/text()").get(),
        #     "forening": ul_properties.xpath("./li/span[text()='Bostadsrättsförening']"
        #                                     "/following-sibling::span/descendant-or-self::a/text()").get()
        # }
