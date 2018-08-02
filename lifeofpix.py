#!/usr/bin/env python3
# encoding=utf-8

"""
爬取lifeofpix网站下载量大于500的图片
实现了最简单的爬虫功能，代码非常具有代表性
代码的详细解释请参考我的博文：https://panqiincs.me/2017/08/13/python-crawler-lifeofpix/
"""

import os
import re
import shutil
import requests
from bs4 import BeautifulSoup

HOME_URL = "http://www.lifeofpix.com/"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}


def image_info(url):
    '''Get infomation of the image: download_url, number of likes, downloads and views.'''

    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    image_url = soup.find('img', attrs={'id': 'pic'})['src']
    image_data = soup.find('div', attrs={'class': 'col-md-3 col-md-offset-1 data'})
    for div in image_data.find_all('div'):
        image_detail = div.getText()
        # 'likes', 'downloads', 'views' are more often, but when equals 0 or 1, no 's'
        if 'like' in image_detail:
            image_likes = int(re.sub("\D", "", image_detail))
        if 'download' in image_detail:
            image_downloads = int(re.sub("\D", "", image_detail))
        if 'view' in image_detail:
            image_views = int(re.sub("\D", "", image_detail))

    print('    ', 'url:', image_url)
    print('    ', 'likes:', image_likes)
    print('    ', 'downloads:', image_downloads)
    print('    ', 'views:', image_views)

    return image_url, image_likes, image_downloads, image_views


def download_image(down_url, filename):
    '''Given a download link, save image to disk.'''

    response = requests.get(down_url, stream=True)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def get_filename(info_url, down_url):
    '''Create a filename from image info url and image download url
    e.g, info_url -- http://www.lifeofpix.com/photo/bouquet/
         down_url -- http://www.lifeofpix.com/wp-content/uploads/2017/04/summer-weddings-1.jpg
    Filename will be images/bouquet.jpg, if such filename already exists, add a number after
    prefix "bouquet", increase the number until filename does not exist.
    '''

    prefix = info_url.split('/')[-2]
    suffix = down_url.split('.')[-1]
    filename = 'images/' + prefix + suffix
    num = 0
    while os.path.exists(filename):
        filename = 'images/' + prefix + str(num) + suffix
        num = num + 1
    return filename


def page_n(url):
    '''Download all images on this page.'''

    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    image_info_total = soup.find_all('a', attrs={'class': 'clickarea overlay'})
    for item in image_info_total:
        image_info_url = item['href']
        if 'lifeofpix' in image_info_url:
            print('  ', image_info_url)
            url, likes, downloads, views = image_info(image_info_url)
            if downloads > 500:
                filename = get_filename(image_info_url, url)
                download_image(url, filename)
                print('  ', filename, 'saved to disk')


def home_page(url, pages=10):
    '''Get total numbers of pages, process each page in order.'''

    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    pages_total = int(soup.find('div', attrs={'class': 'total'}).getText())
    if pages > pages_total:
        pages = pages_total
    print('There are', pages_total, 'pages in total')
    print('Now we query', pages, 'pages of them')

    for i in range(1, pages_total+1):
        page_url = HOME_URL + 'page/' + str(i) + '/'
        print('Processing page', i, ', url:', page_url)
        page_n(page_url)


def main():
    path = os.getcwd()
    path = os.path.join(path, 'images')
    if not os.path.exists(path):
        os.mkdir(path)

    url = HOME_URL
    home_page(url)


if __name__ == '__main__':
    main()

