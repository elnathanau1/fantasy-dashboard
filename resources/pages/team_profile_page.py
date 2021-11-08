from main_dash import app
from resources.services.espn_fantasy_service import get_team, get_team_player_positions
from dash import html, dcc
from dash.dependencies import Input, Output
from resources.constants import *
from resources.util import dropdown_teams_list
from resources.modules.player_stats_table import generate_player_stats_table


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
        return [
            html.H1(children=team_name),
            generate_player_stats_table(team_id),
            html.P('Data from basketballmonster.com')
        ]

    team_name = get_team(int(team_id)).team_name
    team_player_positions = get_team_player_positions(int(team_id))
    return [
        html.H1(children=team_name),
        generate_player_stats_table(team_id),
        html.P('Data from basketballmonster.com'),
        html.H2('Positional Breakdown:'),
        html.Ul(list(
            map(
                lambda pos: html.Li(f'{pos}: {team_player_positions[pos]}'),
                team_player_positions.keys()
            )
        ))
    ]

