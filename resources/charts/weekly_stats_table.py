import pandas as pd
from dash import dash_table
from resources.constants import CATEGORIES

DISPLAY_COLUMNS = ['Team', 'FG%', 'FT%', '3PTM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']
COLOR_SCALE = ['#079B00', '#5CD856', '#ABE5A8', '#DB9D9D', '#E70B0B']
PERCENTILE = [[0, 0.2], [0.2, 0.4], [0.4, 0.6], [0.6, 0.8], [0.78, 1]]


def generate_weekly_stats_table(power_rankings):
    flatten_stats = []
    for team in power_rankings:
        new_row = {'Team': team['team']}
        for cat in CATEGORIES:
            new_row[cat] = round(team['stats'][cat], ndigits=4)
        flatten_stats.append(new_row)

    stats_df = pd.DataFrame(flatten_stats)[DISPLAY_COLUMNS]

    styles = []
    for i in range(0, len(PERCENTILE)):
        styles.append({
            'if': {
                'filter_query': '{{{}}} <= {}'.format(col, value),
                'column_id': col
            },
            'backgroundColor': COLOR_SCALE[i],
            'color': 'white'
        } for (col, value) in stats_df.quantile(PERCENTILE[i]).iteritems())

    return dash_table.DataTable(
        data=stats_df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in stats_df.columns],
        # style_data_conditional=styles, // TODO: COMMENTED BECAUSE BROKEN AT THE MOMENT
        style_cell={'textAlign': 'center'},
    )
