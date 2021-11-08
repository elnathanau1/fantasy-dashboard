from main_dash import app
from resources.services.espn_fantasy_service import get_team, get_team_player_positions
from dash import html, dcc
from dash.dependencies import Input, Output
from resources.constants import *
from resources.util import dropdown_teams_list
from resources.modules.player_stats_table import generate_player_stats_table

PUNT_CHECKLIST_ID = 'punt_checklist_id'
TEAM_PAGE_STATS_TABLE_CONTAINER = 'team_page_stats_table_container'


def generate_team_profile_page():
    return html.Div([
        dcc.Dropdown(
            id=TEAM_SELECTION_DROPDOWN_ID,
            options=dropdown_teams_list(),
            value='1'
        ),
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id=TEAM_PAGE_CONTAINER)
        )
    ])


@app.callback(Output(TEAM_PAGE_CONTAINER, 'children'),
              Input(TEAM_SELECTION_DROPDOWN_ID, 'value'))
def render_team_page_container(team_id):
    # if team_id == 'FREE AGENT':
    #     team_name = 'Free Agents'
    #     return [
    #         html.H1(children=team_name),
    #         generate_player_stats_table(team_id),
    #         html.P('Data from basketballmonster.com')
    #     ]

    team_name = get_team(int(team_id)).team_name
    team_player_positions = get_team_player_positions(int(team_id))
    return [
        html.H1(children=team_name),
        punt_checklist_div(),
        html.Div(id=TEAM_PAGE_STATS_TABLE_CONTAINER),
        # generate_player_stats_table(team_id),
        # html.P('Data from basketballmonster.com'),
        html.H2('Positional Breakdown:'),
        html.Ul(list(
            map(
                lambda pos: html.Li(f'{pos}: {team_player_positions[pos]}'),
                team_player_positions.keys()
            )
        ))
    ]


def punt_checklist_div():
    return html.Div([
        html.P("Punt Categories"),
        dcc.Checklist(
            id=PUNT_CHECKLIST_ID,
            options=[
                {'label': 'PTS', 'value': 'pV'},
                {'label': '3', 'value': '3V'},
                {'label': 'REB', 'value': 'rV'},
                {'label': 'AST', 'value': 'aV'},
                {'label': 'STL', 'value': 'sV'},
                {'label': 'BLK', 'value': 'bV'},
                {'label': 'FG%', 'value': 'fg%V'},
                {'label': 'FT%', 'value': 'ft%V'},
                {'label': 'TO', 'value': 'toV'},
            ],
            value=[],
            labelStyle={'display': 'inline-block'}
        )
    ])


@app.callback(Output(TEAM_PAGE_STATS_TABLE_CONTAINER, 'children'),
              Input(TEAM_SELECTION_DROPDOWN_ID, 'value'),
              [Input(component_id=PUNT_CHECKLIST_ID, component_property='value')])
def render_team_page_container(team_id, punts):
    if len(punts) != 0:
        punt_weights = {}
        for cat in PUNT_ORIGINAL_WEIGHTS:
            if cat not in punts:
                punt_weights[cat] = 1
        return [generate_player_stats_table(team_id, punt_weights)]
    return [generate_player_stats_table(team_id)]


