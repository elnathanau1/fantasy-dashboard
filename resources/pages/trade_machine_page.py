from dash import html, dcc
from resources.modules.trade_machine import generate_trade_machine
from resources.services.espn_fantasy_service import get_league_obj, get_player_stats
from dash.dependencies import Input, Output
from main_dash import app

TRADE_MACHINE_ID = "trade_machine_id"
TRADE_MACHINE_PAGE_ID = "trade_machine_page_id"


def generate_trade_machine_page():
    return html.Div(
        id=TRADE_MACHINE_PAGE_ID,
        children=[
            html.H1(children=get_league_obj().settings.name, style={'textAlign': 'center'}),
            html.H2('Trade Machine', style={'textAlign': 'center'}),
            dcc.Loading(
                id="loading-2",
                type="default",
                children=html.Div(id=TRADE_MACHINE_ID)
            )
        ],
        style={'width': '95vw', 'height': '80vh'}
    )


@app.callback(Output(TRADE_MACHINE_ID, 'children'),
              Input(TRADE_MACHINE_PAGE_ID, 'value'))
def weekly_power_rankings_callback(value):
    get_player_stats()  # refresh cache
    return generate_trade_machine()
