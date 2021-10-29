from main_dash import app
from resources.espn_fantasy_service import get_league_obj, get_team, get_player_stats
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
from resources.constants import *


def generate_team_profile_page():
    league_obj = get_league_obj()
    return html.Div([
        dcc.Dropdown(
            id=TEAM_SELECTION_DROPDOWN_ID,
            options=list(map(lambda team_id: {
                'label': get_team(team_id).team_name,
                'value': str(team_id)
            }, range(1, len(league_obj.teams)))),
            value='1'
        ),
        html.Div(id=TEAM_PAGE_CONTAINER)
    ])


@app.callback(Output(TEAM_PAGE_CONTAINER, 'children'),
              Input(TEAM_SELECTION_DROPDOWN_ID, 'value'))
def render_team_page_container(team_id):
    team_name = get_team(int(team_id)).team_name
    stats_df = get_player_stats()
    team_stats_df = stats_df[stats_df['Fantasy Team'] == team_name]

    columns = list(stats_df.columns)
    columns.remove('espn_id')
    columns.remove('Fantasy Team')

    return [
        html.H1(children=team_name),
        dash_table.DataTable(
            data=team_stats_df.to_dict('records'),
            sort_action='native',
            columns=[{'name': i, 'id': i} for i in columns],
        )
    ]
