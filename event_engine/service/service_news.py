import os
import random
import time
from basic_util.log import dlog
from tarantula.utils.headers import UserHeaders
from tarantula.downloader.news_downloader import NENewsSpider
from tarantula.parser.ne_news_parser import ne_news_parser, ne_article_parser
from tarantula.parser.parser_utils import export_article_to_xml
from redis import StrictRedis

NE_NEWS_PATH = '/data1/file_data/news/163'

def service_set_news_source():
    """
    v1.0 该算法未解决重复爬取的低效率问题，也未解决深度与广度优先级的问题。需要进一步优化。
    """
    rds = StrictRedis(db=4, decode_responses=True)
    downloader = NENewsSpider()
    user_headers = UserHeaders()
    start_url = "https://money.163.com"
    html = downloader.download(url=start_url, headers = user_headers())
    ne_news_parser(rds, html)
    url_len = rds.scard('news_source')
    for i in range(url_len):
        url = rds.spop('news_source')
        print(url)
        html = downloader.download(url=url, headers = user_headers())
        if html is not None:
            ne_news_parser(rds, html)
        time.sleep(random.randint(3, 7))


def service_download_news():
    downloader = NENewsSpider()
    user_headers = UserHeaders()
    rds = StrictRedis(db=4, decode_responses=True)
    urls = rds.smembers('article_page')
    for url in urls:
        html = event_download_news(downloader, url, user_headers())
        time.sleep(random.randint(3, 7))

@dlog
def event_download_news(downloader: NENewsSpider, url: str, headers ):
    # url = "https://www.163.com/dy/article/HIV16DVE05534K6X.html"
    html = downloader.download(url, headers) 
    # ne_news_parser(html, 's')
    title, post_time, content = ne_article_parser(html)
    file_name = os.path.join(NE_NEWS_PATH, post_time[:7], f"{title}.xml")
    export_article_to_xml(file_name, title, post_time, url, content)