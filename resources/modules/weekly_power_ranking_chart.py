from resources.services.espn_fantasy_service import get_week_matchup_stats, get_league_obj
import plotly.express as px
from dash import dcc
import pandas as pd


def generate_weekly_power_ranking_chart():
    league = get_league_obj()
    last_matchup_period = league.currentMatchupPeriod
    rankings = {
        'Week': range(1, last_matchup_period + 1)
    }
    for i in range(1, last_matchup_period + 1):
        week_matchup_stats = get_week_matchup_stats(i)
        for j in range(0, len(week_matchup_stats)):
            team = week_matchup_stats[j]['team']
            if team in rankings.keys():
                rankings[team].append(j + 1)
            else:
                rankings[team] = [j + 1]

    df = pd.DataFrame.from_dict(rankings)

    fig = px.line(df, x='Week', y=df.columns, labels={"variable": "Team"})
    fig.update_yaxes(
        nticks=len(league.teams),
        range=[1, len(league.teams)],
        autorange="reversed",
        title_text='Power Rank',
        fixedrange=True,
        tick0=1,
        dtick=1
    )
    fig.update_xaxes(
        nticks=20,
        range=[1, 20],
        fixedrange=True
    )
    return dcc.Graph(
        id='weekly_power_rankings_graph',
        figure=fig,

    )
