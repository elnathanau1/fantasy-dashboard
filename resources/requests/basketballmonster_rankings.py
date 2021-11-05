import requests
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup

BASKETBALLMONSTER_RANKINGS = "https://basketballmonster.com/playerrankings.aspx"


def get_basketballmonster_rankings() -> DataFrame:
    s = requests.Session()
    # first call gets form session details, second call gets all players
    r = s.post(BASKETBALLMONSTER_RANKINGS)
    soup = BeautifulSoup(r.text, 'html.parser')

    asp_net_hidden = soup.find('form', {'id': 'form1'})
    form = {
        'hiddenInputToUpdateATBuffer_CommonToolkitScripts': 1,
        'TeamFilterControl': 0,
        'StatDisplayType': 'PerGame',
        'ValueDisplayType': 'PerGame',
        'HomeAwayFilterControl': 'HA',
        'DataSetControl': 120,
        'PlayerFilterControl': 'AllPlayers'
    }
    for input in asp_net_hidden.find_all('input', {'type': 'hidden'}):
        form[input['name']] = input.get('value') if input.get('value') is not None else ''

    form['__EVENTTARGET'] = 'PlayerFilterControl'
    form['PositionsFilterControl3'] = 'on'
    form['PositionsFilterControl4'] = 'on'
    form['PositionsFilterControl5'] = 'on'
    form['PositionsFilterControl6'] = 'on'
    form['PositionsFilterControl7'] = 'on'

    r = s.post(BASKETBALLMONSTER_RANKINGS, data=form)
    soup = BeautifulSoup(r.text, 'html.parser')

    # get ranking table and turn into df
    results_table = soup.find('div', {'class': 'results-table'}).find('table')
    df = pd.read_html(results_table.prettify())[0]

    # get ranking table and turn into df
    results_table = soup.find('div', {'class': 'results-table'}).find('table')
    df = pd.read_html(results_table.prettify())[0]

    # remove header rows from df
    header_rows = df[df['Round'] == 'Round'].index
    df = df.drop(header_rows)

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

    return df