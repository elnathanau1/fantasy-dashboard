from datetime import date
from dateutil.parser import parse
import pytz
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup
import requests
from typing import Optional

est = pytz.timezone('US/Eastern')
fmt = '%B %d, %Y %-I:%M %p %Z'


def techoreels_src_link(techoreels_link: str) -> Optional[str]:
    r = requests.get(techoreels_link)
    soup = BeautifulSoup(r.text, 'html.parser')
    input_link = soup.find('input', {'id': 'myInput'})
    if input_link is None:
        return None
    return input_link['value']


def scrape_techoreels_sitemap() -> Optional[DataFrame]:
    try:
        r = requests.get('https://techoreels.com/schedule/nbastreams/')
        soup = BeautifulSoup(r.text, 'html.parser')
        main = soup.find('main')
        links = main.find_all('a')
        link_list = []
        for link in links:
            href = link['href']
            text = link.text.strip()
            if text != '-':
                link_list.append({
                    'game': text.lower(),
                    'url': f'https://techoreels.com/{href}'
                })
        df = DataFrame.from_dict(link_list)
        return df
    except:
        return None
