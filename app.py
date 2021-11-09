from main_dash import app
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from resources.services.espn_fantasy_service import get_league_obj
from resources.pages.team_profile_page import generate_team_profile_page
from resources.pages.week_page import generate_week_page
from resources.pages.league_home_page import generate_league_home_page
from resources.pages.trade_machine_page import generate_trade_machine_page
from resources.pages.streams_page import generate_streams_page
from resources.constants import *


league = get_league_obj()
app.layout = html.Div([
    dcc.Dropdown(
        id=MAIN_NAV_DROPDOWN,
        options=[
            {'label': 'League Home', 'value': 'League Home'},
            {'label': 'Team Pages', 'value': 'Team Pages'},
            {'label': 'Week Summaries', 'value': 'Week Summaries'},
            {'label': 'Trade Machine', 'value': 'Trade Machine'},
            {'label': 'Streams', 'value': 'Streams'}
        ],
        value='League Home'
    ),
    html.Div(id=MAIN_NAV_OUTPUT_CONTAINER)
    ])
server = app.server


@app.callback(Output(MAIN_NAV_OUTPUT_CONTAINER, 'children'),
              Input(MAIN_NAV_DROPDOWN, 'value'))
def render_week_output_container(page):
    if page == 'League Home':
        return [generate_league_home_page()]
    elif page == 'Team Pages':
        return [generate_team_profile_page()]
    elif page == 'Week Summaries':
        return [generate_week_page()]
    elif page == 'Trade Machine':
        return [generate_trade_machine_page()]
    elif page == 'Streams':
        return [generate_streams_page()]


if __name__ == '__main__':
    app.run_server(debug=True)
