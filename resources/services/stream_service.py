from datetime import datetime
from dateutil.parser import parse
import pytz
import requests
from resources.requests.weakstreams_links import weakstream_src_link, scrape_weakstreams_sitemap
from resources.requests.techoreels_stream_links import techoreels_src_link, scrape_techoreels_sitemap
from resources.requests.givemenbastreams_stream_links import givemenbastreams_src_link, scrape_givemenbastreams_sitemap

est = pytz.timezone('US/Eastern')
fmt = '%B %d, %Y %-I:%M %p %Z'


def get_today_game_streams() -> list:
    weakstreams_df = scrape_weakstreams_sitemap()
    techoreels_df = scrape_techoreels_sitemap()
    givemenbastreams_df = scrape_givemenbastreams_sitemap()

    r = requests.get(
        'https://site.api.espn.com/apis/fantasy/v2/games/fba/games',
        params={'dates': datetime.now(pytz.timezone('US/Pacific')).strftime('%Y%m%d')}
    )
    games_json = r.json()
    games = list(map(
        lambda game: {
            'id': game['id'],
            'date': parse(game['date'], fuzzy=True).astimezone(est).strftime(fmt),
            'detail': game['fullStatus']['type']['detail'],
            'percent_complete': game['percentComplete'],
            'teams': list(map(lambda team: team['name'], game['competitors'])),
            'score': list(map(lambda team: team['score'], game['competitors'])),
        },
        games_json['events']
    ))
    games.sort(key=lambda game: parse(game['date'], fuzzy=True))

    game_stream_list = []
    for game in games:
        new_row = {
            'id': game['id'],
            'name': f"{game['teams'][0]} vs {game['teams'][1]} - {game['date']}",
            'streams': []
        }

        # add weakstream
        if weakstreams_df is not None:
            teams = list(map(lambda team: team.lower().replace(' ', '-'), game['teams']))
            result_df = weakstreams_df[
                weakstreams_df['loc'].str.contains(teams[0]) & weakstreams_df['loc'].str.contains(teams[1])]

            urls = list(map(lambda link: weakstream_src_link(link), result_df['loc'].to_list()))
            urls = [x for x in urls if x is not None]
            if len(urls) > 0:
                new_row['streams'].append({
                    'name': 'WEAKSTREAMS',
                    'stream_url': urls[-1]
                })

        # add techoreels
        if techoreels_df is not None:
            teams = list(map(lambda team: team.lower(), game['teams']))
            result_df = techoreels_df[techoreels_df['game'].str.contains(teams[0]) | techoreels_df['game'].str.contains(teams[1])]
            urls = list(map(lambda link: techoreels_src_link(link), result_df['url'].to_list()))
            urls = [x for x in urls if x is not None]
            if len(urls) > 0:
                new_row['streams'].append({
                    'name': 'TECHOREELS',
                    'stream_url': urls[-1]
                })

        # add givemenbastreams
        if givemenbastreams_df is not None:
            teams = list(map(lambda team: team.lower(), game['teams']))
            result_df = givemenbastreams_df[
                givemenbastreams_df['game'].str.contains(teams[0]) | givemenbastreams_df['game'].str.contains(teams[1])]
            urls = list(map(lambda link: givemenbastreams_src_link(link), result_df['url'].to_list()))
            urls = [x for x in urls if x is not None]
            if len(urls) > 0:
                new_row['streams'].append({
                    'name': 'GIVEMENBASTREAMS',
                    'stream_url': urls[-1]
                })

        if len(new_row['streams']) > 0:
            game_stream_list.append(new_row)

    return game_stream_list
