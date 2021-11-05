import datetime

from resources.espn_fantasy_service import *
from dash import html, dcc
import calendar


def generate_schedule_table(team_id):
    current_week = get_league_obj().currentMatchupPeriod
    schedule_df = get_schedule(current_week)
    team_players = get_player_stats()
    return html.Div([
        html.P("Current week is: ")
    ])

