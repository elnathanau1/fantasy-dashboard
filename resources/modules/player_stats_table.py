from resources.services.espn_fantasy_service import get_team, get_player_stats
from dash import dash_table
from resources.constants import *
from resources.util import get_color, append_agg_stats_to_stats_table
from pandas import DataFrame, Series


def generate_player_stats_table(team_id, punt_weights: dict = None):
    style_cats = ['pV', '3V', 'rV', 'aV', 'sV', 'bV', 'fg%V', 'ft%V', 'toV']
    if team_id == 'FREE AGENT':
        stats_df = get_player_stats()
        team_stats_df = stats_df[stats_df['Fantasy Team'] == 'FREE AGENT'].head(FREE_AGENT_TABLE_SIZE)
    else:
        team_name = get_team(int(team_id)).team_name
        stats_df = get_player_stats().copy(deep=True)

        if punt_weights is None:
            style_cats.append('Value')
        else:
            stats_df = apply_punts(stats_df, punt_weights)
            style_cats.append('PuntV')
            style_cats.append('LeagV')
            style_cats.append('Punt+')

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
            , style_cats
        ))
        for new_style in new_styles:
            style.append(new_style)

    return dash_table.DataTable(
        data=team_stats_df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in columns],
        style_data_conditional=style
    )


def calc_weighted_avg(row: Series, weights: dict):
    avg = 0.0
    nonzero = 0.0
    for cat in weights.keys():
        if weights[cat] != 0:
            avg += weights[cat] * float(row[cat])
            nonzero += 1

    return avg / nonzero


def apply_punts(df: DataFrame, punt_weights: dict) -> DataFrame:
    df['LeagV'] = df.apply(lambda row: round(calc_weighted_avg(row, PUNT_ORIGINAL_WEIGHTS), 2), axis=1)
    df['PuntV'] = df.apply(lambda row: round(calc_weighted_avg(row, punt_weights), 2), axis=1)
    df['Punt+'] = df.apply(lambda row: round(row['PuntV'] - row['LeagV'], 2), axis=1)
    df['Rank'] = df['PuntV'].rank(method='first', ascending=False).astype(int)
    df['Round'] = df.apply(lambda row: int((row['Rank'] + 11)/12), axis=1)

    df = df.sort_values(by=['Rank'])
    columns = ['Round', 'Rank', 'LeagV', 'PuntV', 'Punt+', 'Name', 'Inj', 'Team', 'Pos', 'g', 'm/g',
           'p/g', '3/g', 'r/g', 'a/g', 's/g', 'b/g', 'fg%', 'fga/g', 'ft%',
           'fta/g', 'to/g', 'pV', '3V', 'rV', 'aV', 'sV', 'bV', 'fg%V', 'ft%V',
           'toV', 'espn_id', 'Fantasy Team']

    return df[columns]
