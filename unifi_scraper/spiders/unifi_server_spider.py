import scrapy
from unifi_scraper.items import UnifiDownloadItem
from scrapy_playwright.page import PageMethod # Import PageMethod

class UnifiServerSpider(scrapy.Spider):
    name = "unifi_server"
    # allowed_domains is less critical when Playwright navigates, but good for Scrapy's offsite middleware if used.
    allowed_domains = ["ui.com", "dl.ui.com"] 
    
    start_urls = ["https://ui.com/download/releases/network-server"]

    def start_requests(self):
        """
        This method is called by Scrapy when the spider is started.
        It yields scrapy.Request objects that will be handled by scrapy-playwright.
        """
        for url in self.start_urls:
            self.logger.info(f"Requesting URL with Playwright: {url}")
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,  # Tells scrapy-playwright to handle this request
                    "playwright_include_page": True,  # Makes the Playwright page object available in errback
                    "playwright_page_methods": [
                        # Attempt to click the "Accept All" cookie button if it appears.
                        # The selector 'button#onetrust-accept-btn-handler' is common for OneTrust cookie banners.
                        # We'll make this attempt non-critical by not waiting indefinitely or erroring if not found immediately,
                        # as the page might sometimes load without it or with a different banner.
                        PageMethod("evaluate", "() => { const btn = document.querySelector('button#onetrust-accept-btn-handler'); if (btn) { btn.click(); return true; } return false; }"),
                        # Wait for a reasonable time to allow JavaScript to load content.
                        # This might need adjustment. Waiting for a specific element that indicates content readiness is better.
                        # For example, if downloads appear in a div with id="downloads-container":
                        # PageMethod("wait_for_selector", "#downloads-container", timeout=30000), # 30 seconds
                        PageMethod("wait_for_timeout", 10000) # Wait 10 seconds for JS to execute and content to load
                    ],
                    "playwright_context_kwargs": {
                        "ignore_https_errors": True, # Useful for some sites or dev environments
                    },
                },
                callback=self.parse,
                errback=self.errback_playwright, # Custom error handler for Playwright requests
            )

    async def errback_playwright(self, failure):
        """
        Handles errors that occur during Playwright requests.
        It's important to close the Playwright page if it exists in the metadata.
        """
        self.logger.error(f"Playwright Request Error for {failure.request.url}: {failure.value}")
        page = failure.request.meta.get("playwright_page")
        if page and not page.is_closed():
            try:
                await page.close()
                self.logger.info(f"Playwright page for {failure.request.url} closed after error.")
            except Exception as e:
                self.logger.error(f"Error closing Playwright page for {failure.request.url} after initial error: {e}")

    def parse(self, response):
        """
        Parses the UniFi Network Server releases page after JavaScript rendering by Playwright.
        """
        self.logger.info(f"Parsing response from {response.url} (status: {response.status}) after Playwright processing.")

        # To debug, save the HTML that Scrapy sees after Playwright rendering:
        # from pathlib import Path
        # file_path = Path(f"{self.name}_response_playwright.html")
        # file_path.write_bytes(response.body)
        # self.logger.info(f"Saved Playwright-rendered HTML to {file_path.resolve()}")

        # Revised XPath to find the Linux .deb download link.
        # This targets <a> tags with hrefs that:
        # 1. Are hosted on 'dl.ui.com' (Ubiquiti's download domain).
        # 2. Contain 'unifi' in the path (specific to UniFi products).
        # 3. End with common UniFi Linux package names like '_sysvinit_all.deb', '_debian_all.deb', etc.
        # This XPath tries to be specific to the UniFi Network Application for Debian/Ubuntu.
        download_url_xpath = (
            "//a[contains(@href, 'dl.ui.com/') and "
            "contains(@href, '/unifi/') and "
            "(contains(@href, '_sysvinit_all.deb') or "
            "contains(@href, '_debian_all.deb') or "
            "contains(@href, 'unifi_network-application_') and contains(@href, '_all.deb')) " # More recent naming
            "]/@href"
        )
        
        all_matching_links = response.xpath(download_url_xpath).getall()
        self.logger.info(f"Found potential .deb links with primary XPath: {all_matching_links}")

        download_url = None
        if all_matching_links:
            # Often the latest version is listed first, or has a higher version number embedded.
            # For simplicity, we'll take the first one. If multiple are found and a more specific
            # choice is needed, further logic to parse versions from URLs or surrounding text would be required.
            download_url = all_matching_links[0] 
            self.logger.info(f"Selected download URL (first match): {download_url}")
        else:
            # Fallback: A slightly more general XPath if the specific one fails
            fallback_xpath = "//a[contains(@href, 'dl.ui.com/') and contains(@href, '/unifi/') and contains(@href, '.deb')]/@href"
            all_fallback_links = response.xpath(fallback_xpath).getall()
            self.logger.info(f"Primary XPath failed. Found potential .deb links with fallback XPath: {all_fallback_links}")
            if all_fallback_links:
                download_url = all_fallback_links[0] # Take the first from fallback
                self.logger.info(f"Selected download URL (first fallback match): {download_url}")


        if download_url:
            item = UnifiDownloadItem()
            item['software_name'] = 'UniFi Network Server' # Or "UniFi Network Application"
            item['platform'] = 'Linux (Debian/Ubuntu)' 
            item['download_url'] = response.urljoin(download_url) # Ensure it's an absolute URL
            
            # The 'version' field will be populated by the ExtractVersionFromUrlPipeline
            item['version'] = 'Unknown' # Placeholder, pipeline will try to extract
            
            self.logger.info(f"Yielding item: {item}")
            yield item
        else:
            self.logger.error(
                f"All XPath attempts failed to find a suitable Linux .deb download URL on {response.url} "
                "even after Playwright rendering."
            )
            self.logger.warning(
                "This could be due to: \n"
                "1. Significant changes in the website's HTML structure or download link patterns. \n"
                "2. The cookie banner interaction or wait times needing adjustment. \n"
                "3. The target links not being available under the 'network-server' category anymore. \n"
                "Consider inspecting the saved '{self.name}_response_playwright.html' (if uncommented) "
                "or using 'scrapy shell' with Playwright enabled for this URL to test XPaths live."
            )


