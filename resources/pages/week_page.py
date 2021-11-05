import datetime

from main_dash import app
from resources.services.espn_fantasy_service import get_league_obj, get_week_matchup_stats
from dash import html, dcc
from dash.dependencies import Input, Output
from resources.constants import *
from resources.modules.matchup_table import generate_matchup_table
from resources.modules.weekly_stats_table import generate_weekly_stats_table
from resources.modules.weekly_stats_rank_table import generate_weekly_stats_rank_table
from resources.modules.schedule_table import generate_schedule_table

from datetime import date
import datetime


def generate_week_page():
    league_obj = get_league_obj()
    return html.Div([
        dcc.Dropdown(
            id=WEEK_DROPDOWN_ID,
            options=get_week_options(),
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
            dcc.Tab(label='Weekly Ranks', value=WEEKLY_STATS_RANK_TAB),
            dcc.Tab(label='Games Played Count', value=WEEKLY_GAMES_PLAYED)
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
            html.P('Select a cell to view matchup details'),
            generate_matchup_table(power_rankings),
            html.Div(id=TEAM_WEEK_COMPARISON_TABLE)
        ]
    elif tab == WEEKLY_STATS_TABLE_TAB:
        return generate_weekly_stats_table(power_rankings)
    elif tab == WEEKLY_STATS_RANK_TAB:
        return generate_weekly_stats_rank_table(power_rankings)
    elif tab == WEEKLY_GAMES_PLAYED:
        return generate_schedule_table(int(week))


def get_week_options():
    full_week_start = date(2021, 10, 25)
    week_options = [{'label': 'Week 1: 10/19-10/24', 'value': '1'}] + list(map(
        lambda i: {
            'label': f'Week {i + 1}: {(full_week_start + datetime.timedelta(7 * (i - 1))).strftime("%m/%d")}-'
                     f'{(full_week_start + datetime.timedelta(7 * (i - 1) + 6)).strftime("%m/%d")}',
            'value': str(i + 1)
        },
        range(1, 21)
    ))
    return week_options
