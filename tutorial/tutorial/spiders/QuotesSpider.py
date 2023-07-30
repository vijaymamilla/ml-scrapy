import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from ..items import QuoteItem
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "https://quotes.toscrape.com/page/1/"
    ]

    def parse(self, response):
        for quote in response.css("div.quote"):
            item = QuoteItem()
            item['text'] = quote.css("span.text::text").get()
            item['author'] = quote.css("small.author::text").get()
            item['tags'] = quote.css("div.tags a.tag::text").getall()
            yield item

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse,errback=self.errback_httpbin)

    def errback_httpbin(self, failure):
        # logs failures
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)
