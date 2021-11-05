from dash import html, dcc
from resources.modules.weekly_power_ranking_chart import generate_weekly_power_ranking_chart
from resources.services.espn_fantasy_service import get_league_obj
from resources.constants import *
from dash.dependencies import Input, Output
from main_dash import app


def generate_league_home_page():
    return html.Div(
        id=LEAGUE_HOME_PAGE_ID,
        children=[
            html.H1(children=get_league_obj().settings.name, style={'textAlign': 'center'}),
            html.Div(
                children=[
                    html.H2('Team Week to Week Power Ranking', style={'textAlign': 'center'}),
                    dcc.Loading(
                        id="loading-2",
                        type="default",
                        children=html.Div(id=WEEKLY_POWER_RANKING_CHART)
                    )
                ]
            ),
            # html.Div(
            #     children=[
            #         html.Div(
            #             children=[
            #                 generate_trade_machine()
            #             ],
            #             style={'width': '95vw', 'height': '80vh'}
            #         ),
            #         # html.Div(
            #         #     children=[
            #         #         html.H3('Trade Block', style={'textAlign': 'center'}),
            #         #         generate_trade_block_chart(get_trade_block())
            #         #     ],
            #         #     style={'width': '30vw', 'height': '80vh'}
            #         # )
            #     ],
            #     style={
            #         'display': 'grid',
            #         'grid-template-columns': '1fr 1fr',
            #         'grid-gap': '20px'
            #     }
            # )
        ])


@app.callback(Output(WEEKLY_POWER_RANKING_CHART, 'children'),
              Input(LEAGUE_HOME_PAGE_ID, 'value'))
def weekly_power_rankings_callback(value):
    return generate_weekly_power_ranking_chart()
