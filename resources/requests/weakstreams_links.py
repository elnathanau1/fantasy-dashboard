from datetime import date

import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup
import requests


def weakstream_src_link(weakstream_link: str) -> str:
    r = requests.get(weakstream_link)
    soup = BeautifulSoup(r.text, 'html.parser')
    iframe = BeautifulSoup(soup.find('textarea').text, 'html.parser')
    return iframe.find('iframe')['src']


def scrape_weakstreams_sitemap() -> DataFrame:
    r = requests.get('http://weakstreams.com/post-sitemap.xml')
    soup = BeautifulSoup(r.text, 'xml')
    df = pd.read_xml(soup.prettify())
    df = df[df['loc'].str.contains("nba-stream")]
    df = df.sort_values(by=['lastmod'])
    df = df[['loc', 'lastmod']]
    return df


def get_today_game_streams() -> list:
    df = scrape_weakstreams_sitemap()

    r = requests.get(
        'https://site.api.espn.com/apis/fantasy/v2/games/fba/games',
        params={'date': date.today().strftime('%Y%m%d')}
    )
    games_json = r.json()
    games = list(map(
        lambda game: {
            'detail': game['fullStatus']['type']['detail'],
            'percent_complete': game['percentComplete'],
            'teams': list(map(lambda team: team['name'], game['competitors'])),
            'score': list(map(lambda team: team['score'], game['competitors'])),
        },
        games_json['events']
    ))
    games.sort(key=lambda game: game['percent_complete'])

    game_stream_list = []
    for game in games:
        teams = list(map(lambda team: team.lower().replace(' ', '-'), game['teams']))
        result_df = df[df['loc'].str.contains(teams[0]) & df['loc'].str.contains(teams[1])]
        stream_url = result_df.iloc[-1]['loc']
        game_stream_list.append({
            'name': f"{game['teams'][0]} vs {game['teams'][1]}",
            'stream_url': weakstream_src_link(stream_url)
        })

    return game_stream_list
