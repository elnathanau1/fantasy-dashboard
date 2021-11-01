from main_dash import app
from resources.espn_fantasy_service import get_league_obj, get_team
from dash import html, dcc
from dash.dependencies import Input, Output
from resources.constants import *
from resources.charts.player_stats_table import generate_player_stats_table


def generate_team_profile_page():
    league_obj = get_league_obj()
    return html.Div([
        dcc.Dropdown(
            id=TEAM_SELECTION_DROPDOWN_ID,
            options=list(map(lambda team_id: {
                'label': get_team(team_id).team_name,
                'value': str(team_id)
            }, range(1, len(league_obj.teams) + 1))) + [{
                'label': 'Free Agents',
                'value': 'FREE AGENT'
            }],
            value='1'
        ),
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id=TEAM_PAGE_CONTAINER)
        ),
        html.P('Data from basketballmonster.com')
    ])


@app.callback(Output(TEAM_PAGE_CONTAINER, 'children'),
              Input(TEAM_SELECTION_DROPDOWN_ID, 'value'))
def render_team_page_container(team_id):
    if team_id == 'FREE AGENT':
        team_name = 'Free Agents'
    else:
        team_name = get_team(int(team_id)).team_name

    return [
        html.H1(children=team_name),
        generate_player_stats_table(team_id)
    ]

