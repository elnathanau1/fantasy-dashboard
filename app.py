import os

import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from resources.espn_fantasy_service import get_power_rankings
from resources.secrets import local_espn_s2, local_swid, local_league_id
from resources.matchup_table import generate_matchup_table
from resources.weekly_stats_table import generate_weekly_stats_table
from espn_api.basketball import League

WEEK_DROPDOWN_ID = 'week_dropdown'
WEEK_OUTPUT_CONTAINER = 'week_output_container'
CHART_TABS_ID = 'chart_tabs'
CHART_TABS_CONTENT = 'chart_tabs_content'
MATCHUP_CHART = 'matchup_chart'
WEEKLY_STATS_TABLE = 'weekly_stats_table'

espn_s2 = os.environ['ESPN_S2'] if os.getenv("ESPN_S2") else local_espn_s2
swid = os.environ['SWID'] if os.getenv("SWID") is not None else local_swid
league_id = os.environ['LEAGUE_ID'] if os.getenv("LEAGUE_ID") is not None else local_league_id
league = League(league_id, 2022, espn_s2, swid)

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div([
    dcc.Dropdown(
        id=WEEK_DROPDOWN_ID,
        options=[
            {'label': 'Week 1: 10/19-10/24', 'value': '1'},
            {'label': 'Week 2: 10/25-10/31', 'value': '2'}
        ],
        value=str(league.currentMatchupPeriod - 1)
    ),
    html.Div(id=WEEK_OUTPUT_CONTAINER)
    ])
server = app.server


@app.callback(Output(WEEK_OUTPUT_CONTAINER, 'children'),
              Input(WEEK_DROPDOWN_ID, 'value'))
def render_chart_tab_content(week):
    power_rankings = get_power_rankings(league, int(week))
    power_rankings_html_list = list(
        map(
            lambda team: html.Li("{0}: {1}".format(team['team'], team['total_record'])),
            power_rankings
        )
    )
    return [
            html.H1(children=league.settings.name),
            html.P(children="Power rankings for Week #{0}".format(week)),
            html.Ol(power_rankings_html_list),
            html.P(
                children="Team records are calculated by using teams' stats for the week and playing against every " +
                         "other team. Record is then created by aggregating the total win/loss/tie counts."
            ),
            dcc.Tabs(id=CHART_TABS_ID, value=MATCHUP_CHART, children=[
                dcc.Tab(label='Matchup Chart', value=MATCHUP_CHART),
                dcc.Tab(label='Weekly Stats', value=WEEKLY_STATS_TABLE),
            ]),
            html.Div(id=CHART_TABS_CONTENT)
        ]


@app.callback(Output(CHART_TABS_CONTENT, 'children'),
              Input(CHART_TABS_ID, 'value'),
              Input(WEEK_DROPDOWN_ID, 'value'))
def render_chart_tab_content(tab, week):
    power_rankings = get_power_rankings(league, int(week))
    if tab == MATCHUP_CHART:
        return generate_matchup_table(power_rankings)
    elif tab == WEEKLY_STATS_TABLE:
        return generate_weekly_stats_table(power_rankings)


if __name__ == '__main__':
    app.run_server(debug=True)
