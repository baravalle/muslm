import logging
import pprint
import scrapy
import re
import sys
from w3lib.html import remove_tags, remove_tags_with_content
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from socket import gethostbyname, gethostname
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from scrapy.http import Request


# from scrapy.spiders import BaseSpider
from w3lib.html import remove_tags
from muslm.items import MuslmItem

# two cases, categories and articles
# top categories are in /news.php?action=listnewsm&id=XX"
# articles are in /news.php?action=show&id=XXXXX
# all other pages are excluded

class News(scrapy.Spider):
    name = "news"
    allowed_domains = ['muslm.org']
    
    custom_settings = {'JOBDIR':"crawls/news"}
    
    visited_links = []
    
    def start_requests(self):
        urls = [
            'http://www.muslm.org/news.php?action=listnews',
            # random page for testing
            'http://www.muslm.org/news.php?action=show&id=20570'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        
 
        print("Visited links:")
        pprint.pprint(self.visited_links)
        
        # getting all the links
        links = response.xpath('//a/@href').extract()
        
        # regular expression to get only the links we need
        link_validator = re.compile("^news\.php\?action=(listnews|show)")

        for link in links:
            if link_validator.match(link) and not link in self.visited_links:
                self.visited_links.append(link)
                
                # getting the absolute link
                full_link = response.urljoin(link)   
                
                # extraction the action parameter
                URL_parse_result = urlparse(full_link)
                URL_params = parse_qs(URL_parse_result[4])    
                            
                self.log("url: %s" % link)
                
                if URL_params["action"]:
                    if URL_params["action"][0] == "listnewsm":
                        self.log("This is a category page, let's keep spidering.")
                        yield Request(full_link, callback=self.parse)
                    elif URL_params["action"][0] == "show":
                        self.log("This is a news page, let's parse it.")
                        yield Request(full_link, callback=self.parse_item)

    def parse_item(self, response):
        """ This function parses a new page.
        @url http://www.muslm.org/news.php?action=show&id=20570
        @returns items 1
        @scrapes date title url project server spider body      
        """
        
        # sanity checks
        URL_parse_result = urlparse(response.url)
        
        # are we in a news page?
        if URL_parse_result[2] == "/news.php":
        
            # extracting the querystring
            URL_params = parse_qs(URL_parse_result[4])    
                        
            self.log("title: %s" % response.xpath('//title/text()').extract())
            
            # is this a news page?
            if URL_params["action"]:
                if URL_params["action"][0] == "show":
        
                    l = ItemLoader(item=MuslmItem(), response=response)
                    l.add_value('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))            
                    l.add_value('project', self.settings.get('BOT_NAME'))
                    l.add_value('spider', self.name)
                    l.add_value('server', gethostname())
                    l.add_xpath('title', '//title/text()', MapCompose(str.strip, str.title), Join())
                    l.add_value('url', response.url)
                    # this would still have lots of garbage - but it's a start. 
                    body = response.xpath('//div[@class="news-container-left-side"]/div[@class="justify"]').extract()[0]
                    
                    # let's clean the body
                    body = remove_tags(remove_tags_with_content(body, ('script',)))
                    body = re.sub(r"\n{2,}" , "\n", body)
                    body = str.replace(body, "\n \nTweet\n", "")    
                   
                    l.add_value('body', body)
#                    l.add_xpath('body', '//div[@class="news-container-left-side"]/div[@class="justify"]', MapCompose(remove_tags, str.strip), Join(), MapCompose(str.strip))
             
                    return l.load_item()  
  
            

