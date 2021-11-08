import requests
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup
from resources.constants import *

HASHTAG_SCHEDULE = 'https://hashtagbasketball.com/advanced-nba-schedule-grid'


def get_schedule(week: int) -> DataFrame:
    s = requests.Session()
    s.headers.update({
        'user-agent': 'Mozilla/5.0'
    })
    r = s.post(HASHTAG_SCHEDULE)
    soup = BeautifulSoup(r.text, 'html.parser')
    inputs = soup.find_all('input', {'type': 'submit', 'class': 'btn'})

    options = list(map(lambda input: {
        'value': input['value'],
        'script_id': input['name']
    }, inputs))[2::]

    form = {}
    for input in soup.find_all('input', {'type': 'hidden'}):
        form[input['name']] = input.get('value') if input.get('value') is not None else ''

    form['ctl00$ScriptManager1'] = 'ctl00$ContentPlaceHolder1$UpdatePanel1|' + options[week-1]['script_id']
    form[options[week - 1]['script_id']] = options[week-1]['value']
    r = s.post(HASHTAG_SCHEDULE, data=form)
    soup = BeautifulSoup(r.text, 'html.parser')

    schedule_table = soup.find('div', {'class': 'table-responsive'}).find('table')
    # get schedule table and turn into df
    df = pd.read_html(schedule_table.prettify())[0]
    # remove header rows from df
    df = df.drop(df[df['Team'] == '# Games Played'].index)
    df = df.drop(df[df['Team'] == 'Team'].index)

    df['Team'] = df['Team'].apply(lambda team: NBA_NAME_TO_ABBREVIATION_MAP[team])
    df.set_index('Team', inplace=True)

    return df
