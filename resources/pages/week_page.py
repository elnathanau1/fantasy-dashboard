from main_dash import app
from resources.espn_fantasy_service import get_league_obj, get_week_matchup_stats
from dash import html, dcc
from dash.dependencies import Input, Output
from resources.constants import *
from resources.charts.matchup_table import generate_matchup_table
from resources.charts.weekly_stats_table import generate_weekly_stats_table
from resources.charts.weekly_stats_rank_table import generate_weekly_stats_rank_table


def generate_week_page():
    league_obj = get_league_obj()
    return html.Div([
        dcc.Dropdown(
            id=WEEK_DROPDOWN_ID,
            options=[
                {'label': 'Week 1: 10/19-10/24', 'value': '1'},
                {'label': 'Week 2: 10/25-10/31', 'value': '2'},
                {'label': 'Week 3: 11/01-11/07', 'value': '3'}
            ],
            value=str(league_obj.currentMatchupPeriod)
        ),
        html.Div(id=WEEK_OUTPUT_CONTAINER)
    ])


@app.callback(Output(WEEK_OUTPUT_CONTAINER, 'children'),
              Input(WEEK_DROPDOWN_ID, 'value'))
def render_week_output_container(week):
    league = get_league_obj()
    week_matchup_stats = get_week_matchup_stats(int(week))
    week_matchup_stats_html_list = list(
        map(
            lambda team: html.Li("{0}: {1}".format(team['team'], team['total_record'])),
            week_matchup_stats
        )
    )
    return [
        html.H1(children=league.settings.name),
        html.P(children="Power rankings for Week #{0}".format(week)),
        html.Ol(week_matchup_stats_html_list),
        html.P(
            children="Team records are calculated by using teams' stats for the week and playing against every " +
                     "other team. Record is then created by aggregating the total win/loss/tie counts."
        ),
        dcc.Tabs(id=CHART_TABS_ID, value=MATCHUP_CHART_TAB, children=[
            dcc.Tab(label='Matchup Chart', value=MATCHUP_CHART_TAB),
            dcc.Tab(label='Weekly Stats', value=WEEKLY_STATS_TABLE_TAB),
            dcc.Tab(label='Weekly Ranks', value=WEEKLY_STATS_RANK_TAB)
        ]),
        html.Div(id=CHART_TABS_CONTENT)
    ]


@app.callback(Output(CHART_TABS_CONTENT, 'children'),
              Input(CHART_TABS_ID, 'value'),
              Input(WEEK_DROPDOWN_ID, 'value'))
def render_chart_tab_content(tab, week):
    power_rankings = get_week_matchup_stats(int(week))
    if tab == MATCHUP_CHART_TAB:
        return [
            generate_matchup_table(power_rankings),
            html.Div(id=TEAM_WEEK_COMPARISON_TABLE)
        ]
    elif tab == WEEKLY_STATS_TABLE_TAB:
        return generate_weekly_stats_table(power_rankings)
    elif tab == WEEKLY_STATS_RANK_TAB:
        return generate_weekly_stats_rank_table(power_rankings)
