import json
import os

import dash
from dash import html
from dash import dcc
import pandas as pd
from resources.espn_fantasy_service import get_power_rankings
from resources.secrets import local_espn_s2, local_swid, local_league_id
from espn_api.basketball import League

espn_s2 = os.environ['ESPN_S2'] if os.environ['ESPN_S2'] is not None else local_espn_s2
swid = os.environ['SWID'] if os.environ['SWID'] is not None else local_swid
league_id = os.environ['LEAGUE_ID'] if os.environ['LEAGUE_ID'] is not None else local_league_id
league = League(league_id, 2022, espn_s2, swid)

power_rankings = get_power_rankings(league, 1)

power_rankings_html_list = list(map(lambda team: html.Li("{0}: {1}".format(team['team'], team['total_record'])), power_rankings))

app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1(children=league.settings.name),
        html.P(
            children="Power rankings for Matchup #{0}".format(1),
        ),
        html.Ol(
            power_rankings_html_list
        )
    ]
)
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
