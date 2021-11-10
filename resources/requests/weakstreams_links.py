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


def weakstream_src_link(weakstream_link: str) -> Optional[str]:
    r = requests.get(weakstream_link)
    soup = BeautifulSoup(r.text, 'html.parser')
    textarea = soup.find('textarea')
    if textarea is None:
        return None
    iframe = BeautifulSoup(textarea.text, 'html.parser')
    return iframe.find('iframe')['src']


def scrape_weakstreams_sitemap() -> DataFrame:
    r = requests.get('http://weakstreams.com/post-sitemap.xml')
    soup = BeautifulSoup(r.text, 'xml')
    df = pd.read_xml(soup.prettify())
    df = df[df['loc'].str.contains("nba-stream")]
    df = df.sort_values(by=['lastmod'])
    df = df[['loc', 'lastmod']]
    return df

