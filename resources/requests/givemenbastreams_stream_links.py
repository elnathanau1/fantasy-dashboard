from pandas import DataFrame
from bs4 import BeautifulSoup
import requests
from typing import Optional


def givemenbastreams_src_link(givemenbastreams_link: str) -> Optional[str]:
    r = requests.get(givemenbastreams_link)
    soup = BeautifulSoup(r.text, 'html.parser')
    textarea = soup.find('textarea')
    if textarea is None:
        return None
    iframe = BeautifulSoup(textarea.text, 'html.parser')
    return iframe.find('iframe')['src']


def scrape_givemenbastreams_sitemap() -> Optional[DataFrame]:
    r = requests.get('http://givemenbastreams.com/nba')
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
        main = soup.find('main')
        links = main.find_all('a')
        link_list = []
        for link in links:
            href = link['href']
            text = link.text.strip().replace('\n', '')
            if text != '-':
                link_list.append({
                    'game': text.lower(),
                    'url': href
                })
        df = DataFrame.from_dict(link_list)
        return df
    except:
        return None

