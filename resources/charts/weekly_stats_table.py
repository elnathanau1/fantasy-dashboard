import pandas as pd
from dash import dash_table
from resources.constants import CATEGORIES
from resources.util import get_color

DISPLAY_COLUMNS = ['Team', 'FG%', 'FT%', '3PTM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']


def generate_weekly_stats_table(power_rankings):
    flatten_stats = []
    for team in power_rankings:
        new_row = {'Team': team['team']}
        for cat in CATEGORIES:
            new_row[cat] = round(team['stats'][cat], ndigits=4)
        flatten_stats.append(new_row)

    stats_df = pd.DataFrame(flatten_stats)[DISPLAY_COLUMNS]

    style = []
    for index, row in stats_df.iterrows():
        new_styles = list(map(
            lambda cat: {
                'if': {
                    'filter_query': '{{{0}}} = {1}'.format(cat, row[cat]),
                    'column_id': cat
                },
                'backgroundColor': get_color(row[cat], stats_df[cat].max(), stats_df[cat].min())
            }
            , ['FG%', 'FT%', '3PTM', 'REB', 'AST', 'STL', 'BLK', 'PTS']
        ))

        for new_style in new_styles:
            style.append(new_style)

        style.append({
            'if': {
                'filter_query': '{{TO}} = {0}'.format(row['TO']),
                'column_id': 'TO'
            },
            'backgroundColor': get_color(-1 * row['TO'], -1 * stats_df['TO'].min(), -1 * stats_df['TO'].max())
        })

    return dash_table.DataTable(
        data=stats_df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in stats_df.columns],
        style_data_conditional=style,
        style_cell={'textAlign': 'center'},
    )
