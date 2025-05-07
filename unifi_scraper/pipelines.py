# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re

class UnifiScraperPipeline:
    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component.
        It prints the scraped item's details.
        """
        print("=" * 60)
        print(f"Software:       {item.get('software_name', 'N/A')}")
        print(f"Platform:       {item.get('platform', 'N/A')}")
        print(f"Version:        {item.get('version', 'N/A')}")
        print(f"Download URL:   {item.get('download_url', 'N/A')}")
        print("=" * 60)
        return item

class ExtractVersionFromUrlPipeline:
    def process_item(self, item, spider):
        """
        This pipeline tries to extract the version from the download URL
        if it wasn't found in the page text.
        This is a common pattern for UniFi download URLs.
        Example: https://dl.ui.com/unifi/8.2.93/unifi_sysvinit_all.deb -> version 8.2.93
        """
        if item.get('version') == 'Unknown' or not item.get('version'):
            url = item.get('download_url')
            if url:
                # Regex to find version like x.y.z or x.y in the path
                # e.g., /8.2.93/ or /7.5/
                match = re.search(r'/([\d\.]+)/', url)
                if match:
                    item['version'] = match.group(1)
        return item

