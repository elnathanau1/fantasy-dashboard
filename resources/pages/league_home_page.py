from dash import html
from resources.charts.trade_block import generate_trade_block_chart
from resources.charts.weekly_power_ranking_chart import generate_weekly_power_ranking_chart
from resources.espn_fantasy_service import get_league_obj, get_trade_block


def generate_league_home_page():
    return html.Div([
        html.H1(children=get_league_obj().settings.name),
        html.Div(
            children=[
                html.H3('Team Week to Week Power Ranking'),
                generate_weekly_power_ranking_chart()
            ],
            style={'width': '70vw'}
        ),
        html.Div(
            children=[
                html.H3('Trade Block', style={'textAlign': 'center'}),
                generate_trade_block_chart(get_trade_block())
            ],
            style={'width': '30vw', 'height': '100vh'}
        )
    ])
