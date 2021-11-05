from resources.services.espn_fantasy_service import get_team, get_player_stats
from dash import dash_table
from resources.constants import *
from resources.util import get_color, append_agg_stats_to_stats_table


def generate_player_stats_table(team_id):
    if team_id == 'FREE AGENT':
        stats_df = get_player_stats()
        team_stats_df = stats_df[stats_df['Fantasy Team'] == 'FREE AGENT'].head(FREE_AGENT_TABLE_SIZE)
    else:
        team_name = get_team(int(team_id)).team_name
        stats_df = get_player_stats()
        team_stats_df = stats_df[stats_df['Fantasy Team'] == team_name]
        team_stats_df = append_agg_stats_to_stats_table(team_stats_df)

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
