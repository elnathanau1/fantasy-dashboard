import pandas as pd
from dash import dash_table
from resources.constants import CATEGORIES
from resources.util import get_colors_stat_tables

DISPLAY_COLUMNS = ['Team', 'FG%', 'FT%', '3PTM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']


def generate_weekly_stats_table(power_rankings):
    flatten_stats = []
    for team in power_rankings:
        new_row = {'Team': team['team']}
        for cat in CATEGORIES:
            new_row[cat] = round(team['stats'][cat], ndigits=4)
        flatten_stats.append(new_row)

    stats_df = pd.DataFrame(flatten_stats)[DISPLAY_COLUMNS]

    return dash_table.DataTable(
        data=stats_df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in stats_df.columns],
        style_data_conditional=get_colors_stat_tables(stats_df),
        style_cell={'textAlign': 'center'},
    )
