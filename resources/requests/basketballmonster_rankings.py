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
        'PlayerFilterControl': 'AllPlayers',
        '__SCROLLPOSITIONX': 0,
        '__SCROLLPOSITIONY': 0,
        'DateFilterControl': 'FullSeason'
        # 'ShowOptionsControlCB': 'on',
        # 'SHOWUsage': 'on',
        # 'SHOWRounds': 'on',
        # 'SHOWPuntColumns': 'on',
        # 'SHOWInjuries': 'on',
        # 'SHOWStats': 'on',
        # 'RANKINGSBUTTON': 'Refresh'
    }
    for input in asp_net_hidden.find_all('input', {'type': 'hidden'}):
        form[input['name']] = input.get('value') if input.get('value') is not None else ''

    form['__EVENTTARGET'] = 'PuntCategoriesControl7'
    form['__EVENTARGUMENT'] = ''
    form['__LASTFOCUS'] = ''
    form['ctl00$MasterNameTB'] = ''
    form['PositionsFilterControl3'] = 'on'
    form['PositionsFilterControl4'] = 'on'
    form['PositionsFilterControl5'] = 'on'
    form['PositionsFilterControl6'] = 'on'
    form['PositionsFilterControl7'] = 'on'

    form['PuntCategoriesControl7'] = 'on'

    headers = {
        'origin': 'https://basketballmonster.com',
        'referer': 'https://basketballmonster.com/playerrankings.aspx'
    }

    r = s.post(BASKETBALLMONSTER_RANKINGS, data=form, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    # get ranking table and turn into df
    results_table = soup.find('div', {'class': 'results-table'}).find('table')
    df = pd.read_html(results_table.prettify())[0]

    # remove header rows from df
    header_rows = df[df['Round'] == 'Round'].index
    df = df.drop(header_rows)

    return df