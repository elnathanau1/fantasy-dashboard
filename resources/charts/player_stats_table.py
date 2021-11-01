from main_dash import app
from resources.espn_fantasy_service import get_league_obj, get_team, get_player_stats
from dash import html, dcc, dash_table
from resources.constants import *
from resources.util import get_color


def generate_player_stats_table(team_id):
    if team_id == 'FREE AGENT':
        team_name = 'Free Agents'
        stats_df = get_player_stats()
        team_stats_df = stats_df[stats_df['Fantasy Team'] == 'FREE AGENT'].head(FREE_AGENT_TABLE_SIZE)
    else:
        team_name = get_team(int(team_id)).team_name
        stats_df = get_player_stats()
        team_stats_df = stats_df[stats_df['Fantasy Team'] == team_name]
        new_row = {
            'Name': 'Avg/Total Values'
        }
        # cats to sum
        for cat in ['Value', 'pV', '3V', 'rV', 'aV', 'sV', 'bV', 'fg%V', 'ft%V', 'toV']:
            new_row[cat] = round(team_stats_df.loc[:, cat].astype(float).sum(), 2)

        for cat in ['m/g', 'p/g', '3/g', 'r/g', 'a/g', 's/g', 'b/g', 'to/g']:
            new_row[cat] = round(team_stats_df.loc[:, cat].astype(float).mean(), 2)

        team_stats_df = team_stats_df.append(new_row, ignore_index=True)

    columns = list(stats_df.columns)
    columns.remove('espn_id')
    columns.remove('Fantasy Team')

    style = []
    for index, row in team_stats_df.iterrows():
        new_styles = list(map(
            lambda cat: {
                'if': {
                    'filter_query': '{{{0}}} = {1}'.format(cat, row[cat]),
                    'column_id': cat
                },
                'backgroundColor': get_color(row[cat], 3.0, -3.0)
            }
            , ['Value', 'pV', '3V', 'rV', 'aV', 'sV', 'bV', 'fg%V', 'ft%V', 'toV']
        ))
        for new_style in new_styles:
            style.append(new_style)

    return dash_table.DataTable(
        data=team_stats_df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in columns],
        style_data_conditional=style
    )
