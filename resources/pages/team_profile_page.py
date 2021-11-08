from main_dash import app
from resources.services.espn_fantasy_service import get_team
from dash import html, dcc
from dash.dependencies import Input, Output
from resources.constants import *
from resources.util import dropdown_teams_list
from resources.modules.player_stats_table import generate_player_stats_table
from resources.modules.schedule_table import generate_schedule_table


def generate_team_profile_page():
    return html.Div([
        dcc.Dropdown(
            id=TEAM_SELECTION_DROPDOWN_ID,
            options=dropdown_teams_list() + [{
                'label': 'Free Agents',
                'value': 'FREE AGENT'
            }],
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
    if team_id == 'FREE AGENT':
        team_name = 'Free Agents'
    else:
        team_name = get_team(int(team_id)).team_name
    return [
        html.H1(children=team_name),
        generate_player_stats_table(team_id),
        html.P('Data from basketballmonster.com')
    ]

