from datetime import datetime
from dateutil.parser import parse
import pytz
import requests
from resources.requests.weakstreams_links import weakstream_src_link, scrape_weakstreams_sitemap
from resources.requests.techoreels_stream_links import techoreels_src_link, scrape_techoreels_sitemap
from resources.requests.givemenbastreams_stream_links import givemenbastreams_src_link, scrape_givemenbastreams_sitemap

est = pytz.timezone('US/Eastern')
fmt = '%B %d, %Y %-I:%M %p %Z'

POSITION_MAP = {
    "1": "PG",
    "2": "SG",
    "3": "SF",
    "4": "PF",
    "5": "C"
}


def get_live_games():
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
            'clock': game['fullStatus']['clock'],
            'percent_complete': game['percentComplete'],
            'teams': list(map(lambda team: team['name'], game['competitors'])),
            'score': list(map(lambda team: team['score'], game['competitors'])),
            'record': list(map(lambda team: team['record'], game['competitors'])),
            'active_lineup': list(map(
                lambda team: list(map(
                    lambda player: {
                        'id': player['playerId'],
                        'position': POSITION_MAP[player['positionId']]
                    },
                    team['active']
                )), game['competitors']
            )),
            'recent_plays': list(filter(None, map(
                lambda play: {
                    'text': play['text'],
                    'short_text': play['shortText'],
                    'period': play['period'],
                    'clock': play['clock'],
                    'player': play['players'][0] if len(play['players']) > 0 else None
                } if 'playId' in play.keys() else None,
                game['recentPlays']
            )))
            # 'active_lineup': [
            #     [
            #         {'id': 3468, 'position': 'PG'},
            #         {'id': 3468, 'position': 'SG'},
            #         {'id': 3468, 'position': 'SF'},
            #         {'id': 3468, 'position': 'PF'},
            #         {'id': 3468, 'position': 'C'},
            #     ],
            #     [
            #         {'id': 3468, 'position': 'PG'},
            #         {'id': 3468, 'position': 'SG'},
            #         {'id': 3468, 'position': 'SF'},
            #         {'id': 3468, 'position': 'PF'},
            #         {'id': 3468, 'position': 'C'},
            #     ]
            # ],
            # 'recent_plays': [
            #     {'text': 'Norman Powell makes 27-foot three point jumper (Damian Lillard assists)',
            #      'short_text': 'test', 'period': 1, 'clock': 531, 'player': '1111'},
            #     {'text': 'test2', 'short_text': 'test', 'period': 2, 'clock': 532, 'player': '1111'},
            #     {'text': 'test3', 'short_text': 'test', 'period': 3, 'clock': 533, 'player': '1111'},
            #     {'text': 'test4', 'short_text': 'test', 'period': 4, 'clock': 534, 'player': '1111'},
            #     {'text': 'test5', 'short_text': 'test', 'period': 5, 'clock': 535, 'player': '1111'}
            # ]
        },
        games_json['events']
    ))
    games.sort(key=lambda game: parse(game['date'], fuzzy=True))
    return games


def get_today_game_streams() -> list:
    weakstreams_df = scrape_weakstreams_sitemap()
    techoreels_df = scrape_techoreels_sitemap()
    givemenbastreams_df = scrape_givemenbastreams_sitemap()

    games = get_live_games()

    game_stream_list = []
    for game in games:
        new_row = {
            'id': game['id'],
            'name': f"{game['teams'][0]} ({game['record'][0]}) vs {game['teams'][1]} ({game['record'][1]}) - {game['date']}",
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


# print(get_live_games())