from espn_api.basketball import League, Team, Matchup
import requests
from dateutil.parser import parse
import datetime
import pytz
import os
from cachetools import TTLCache
from pandas import DataFrame
from resources.requests.basketballmonster_rankings import get_basketballmonster_rankings
from resources.requests.hashtagbasketball_schedule import get_schedule
from resources.services.stream_service import get_today_game_streams

from resources.secrets import *

espn_s2 = os.environ['ESPN_S2'] if os.getenv("ESPN_S2") else local_espn_s2
swid = os.environ['SWID'] if os.getenv("SWID") is not None else local_swid
league_id = os.environ['LEAGUE_ID'] if os.getenv("LEAGUE_ID") is not None else local_league_id

CATEGORIES = ['TO', 'PTS', 'BLK', 'STL', 'AST', 'REB', '3PTM', 'FG%', 'FT%']
PLAYER_MAP_URL = 'https://fantasy.espn.com/apis/v3/games/fba/seasons/2022/players?scoringPeriodId=0&view=players_wl'
LEAGUE_INFO_URL = 'https://fantasy.espn.com/apis/v3/games/fba/seasons/{0}/segments/0/leagues/{1}?view=mRoster&view=mTeam'

cache = TTLCache(maxsize=50, ttl=60 * 60)
LEAGUE_OBJ_KEY = 'league_obj_key'
LEAGUE_INFO_KEY = 'league_info_key'
PLAYER_MAP_KEY = 'player_map_key'
PLAYER_STATS_KEY = 'player_stats_key'
WEEK_SCHEDULE_KEY = 'week_schedule_key'
TODAY_STREAMS_KEY = 'today_streams_key'


def get_league_obj() -> League:
    if LEAGUE_OBJ_KEY not in cache.keys():
        cache[LEAGUE_OBJ_KEY] = League(league_id, 2022, espn_s2, swid)
    return cache[LEAGUE_OBJ_KEY]


def get_week_schedule(week: int) -> DataFrame:
    if WEEK_SCHEDULE_KEY + str(week) not in cache.keys():
        cache[WEEK_SCHEDULE_KEY + str(week)] = get_schedule(week)
    return cache[WEEK_SCHEDULE_KEY + str(week)]


def get_league_info():
    if LEAGUE_INFO_KEY not in cache.keys():
        url = LEAGUE_INFO_URL.format(2022, league_id)
        req = requests.get(
            url,
            headers={'cookie': 'espnAuth={{"swid":"{0}"}}; espn_s2={1};'.format(swid, espn_s2)}
        )
        cache[LEAGUE_INFO_KEY] = req.json()
    return cache[LEAGUE_INFO_KEY]


def get_player_map():
    if PLAYER_MAP_KEY not in cache.keys():
        r = requests.get(
            url=PLAYER_MAP_URL,
            headers={'x-fantasy-filter': '{"filterActive":{"value":true}}'}
        )
        cache[PLAYER_MAP_KEY] = r.json()
    return cache[PLAYER_MAP_KEY]


def get_player_stats() -> DataFrame:
    if PLAYER_STATS_KEY not in cache.keys():
        df = get_basketballmonster_rankings()

        # add espn_player_id to df for ease of use
        player_map = get_player_map()
        df['espn_id'] = df.apply(lambda row: next(
            (player['id'] for player in player_map if
             normalize_name(row['Name']) == normalize_name(player['fullName'])),
            'a'
        ), axis=1)

        # add ownership
        league_info = get_league_info()
        df['Fantasy Team'] = df.apply(lambda row: next(
            ('{0} {1}'.format(team['location'], team['nickname']) \
             for team in league_info['teams'] \
             if row['espn_id'] in list(map(
                lambda roster_entry: roster_entry['playerId'], team['roster']['entries']
            ))),
            'FREE AGENT'
        ), axis=1)

        cache[PLAYER_STATS_KEY] = df
    return cache[PLAYER_STATS_KEY]


def get_today_streams() -> list:
    if TODAY_STREAMS_KEY not in cache.keys():
        cache[TODAY_STREAMS_KEY] = get_today_game_streams()
    return cache[TODAY_STREAMS_KEY]


def normalize_name(name: str):
    # c.j. mccollum
    # kelly oubre jr
    # marcus morris sr
    # robert williams iii
    # kevin knox ii
    # lonnie walker iv
    new_name = name.lower() \
        .replace('.', '') \
        .replace(' jr', '') \
        .replace(' sr', '') \
        .replace(' iii', '') \
        .replace(' ii', '') \
        .replace(' iv', '') \
        .strip()
    return new_name


def get_team(team_id: int) -> Team:
    league = get_league_obj()
    return [team for team in league.teams if team.team_id == team_id][0]


def get_matchup_cats(matchup_period: int, team_id: int):
    team = get_team(team_id)

    current_matchup: Matchup = team.schedule[matchup_period - 1]
    if current_matchup.home_team.team_id == team_id:
        cats = current_matchup.home_team_cats
    else:
        cats = current_matchup.away_team_cats

    cat_dict = {}
    for category in CATEGORIES:
        if cats is None:
            cat_dict[category] = 0
        else:
            cat_dict[category] = cats[category]['score']

    return cat_dict


def compare_team_stats(team_1, team_2):
    return_dict = {
        'home_team': team_1[0],
        'away_team': team_2[0]
    }

    win = []
    lose = []
    tie = []

    for category in CATEGORIES:
        multiplier = 1
        if category == 'TO':
            multiplier = -1

        if team_1[1][category] * multiplier > team_2[1][category] * multiplier:
            win.append(category)
        elif team_1[1][category] * multiplier < team_2[1][category] * multiplier:
            lose.append(category)
        else:
            tie.append(category)

    return_dict.update({
        'win_cats': win,
        'lose_cats': lose,
        'tie_cats': tie,
        'wins': len(win),
        'losses': len(lose),
        'ties': len(tie)
    })

    return return_dict


def get_week_matchup_stats(matchup_period: int):
    if matchup_period == 0:
        return []

    league = get_league_obj()

    team_stats_list = list(
        map(lambda team: [team.team_name, get_matchup_cats(matchup_period, team.team_id)], league.teams))

    results_list = []
    for i in range(0, len(team_stats_list)):
        total_win = 0
        total_lose = 0
        total_tie = 0

        matchup_win = 0
        matchup_lose = 0
        matchup_tie = 0

        matchups = []
        for j in range(0, len(team_stats_list)):
            if j != i:
                result = compare_team_stats(team_stats_list[i], team_stats_list[j])
                total_win += result['wins']
                total_lose += result['losses']
                total_tie += result['ties']
                matchups.append(result)
                if result['wins'] > result['losses']:
                    matchup_win += 1
                elif result['wins'] == result['losses']:
                    matchup_tie += 1
                else:
                    matchup_lose += 1

        results_list.append(
            {
                'team': team_stats_list[i][0],
                'total_record': '{0}-{1}-{2}'.format(total_win, total_lose, total_tie),
                'record_vs_others': '{0}-{1}-{2}'.format(matchup_win, matchup_lose, matchup_tie),
                'score': total_win + total_tie / 2.0,
                'stats': team_stats_list[i][1],
                'matchups': matchups
            }
        )

    return sorted(results_list, key=lambda x: x['score'] * -1)


def get_player_info(player_id: int):
    for player in get_player_map():
        if str(player['id']) == str(player_id):
            return player

    return None


def get_player_headshot(player_id: int):
    return 'https://a.espncdn.com/combiner/i?img=%2Fi%2Fheadshots%2Fnba%2Fplayers%2Ffull%2F{0}.png&w=72&cb=1'.format(
        player_id)


def get_trade_block():
    league_info = get_league_info()
    trade_block = []
    for team in league_info['teams']:
        if 'players' in team['tradeBlock'].keys():
            for player_id in team['tradeBlock']['players'].keys():
                if team['tradeBlock']['players'][player_id] == 'ON_THE_BLOCK':
                    trade_block.append({
                        'player_id': player_id,
                        'team_id': team['id'],
                        'team_name': team['location'] + ' ' + team['nickname']
                    })
    return trade_block


def get_team_player_positions(team_id):
    team = get_team(team_id)
    positions = {
        'PG': 0,
        'SG': 0,
        'SF': 0,
        'PF': 0,
        'C': 0
    }
    for player in team.roster:
        for pos in positions.keys():
            if pos in player.eligibleSlots:
                positions[pos] = positions[pos] + 1

    return positions
