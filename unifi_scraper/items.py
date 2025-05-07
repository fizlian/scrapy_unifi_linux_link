# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class UnifiDownloadItem(scrapy.Item):
    # Field to store the name of the software
    software_name = scrapy.Field()
    # Field to store the platform (e.g., Linux, Debian/Ubuntu)
    platform = scrapy.Field()
    # Field to store the extracted version number
    version = scrapy.Field()
    # Field to store the direct download URL
    download_url = scrapy.Field()

