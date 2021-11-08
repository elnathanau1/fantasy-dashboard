from colour import Color
from resources.services.espn_fantasy_service import get_league_obj
import math


def get_color(val, max_val, min_val):
    val = float(val)
    if math.isnan(val):
        return Color(rgb=(1,1,1)).get_hex_l()
    
    avg = max_val / 2.0 + min_val / 2.0
    if max_val == avg:
        return Color(rgb=(1, 1, 1)).get_hex_l()

    score = abs((max_val - avg) - abs(val - avg)) / (max_val - avg)
    if val > max_val or val < min_val:
        score = 0.0
    elif score > 1.0:
        score = 1.0

    if val > avg:
        return Color(rgb=(score, 1, score)).get_hex_l()
    else:
        return Color(rgb=(1, score, score)).get_hex_l()


def get_colors_stat_tables(df):
    style = []
    for index, row in df.iterrows():
        new_styles = list(map(
            lambda cat: {
                'if': {
                    'filter_query': '{{{0}}} = {1}'.format(cat, row[cat]),
                    'column_id': cat
                },
                'backgroundColor': get_color(row[cat], df[cat].max(), df[cat].min())
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
            'backgroundColor': get_color(-1 * row['TO'], -1 * df['TO'].min(), -1 * df['TO'].max())
        })

    return style


def dropdown_teams_list():
    league_obj = get_league_obj()
    teams = league_obj.teams
    return list(map(lambda team: {
        'label': team.team_name,
        'value': team.team_id
    }, teams))


def append_agg_stats_to_stats_table(stats_df):
    new_row = {
        'Name': 'Avg/Total Values'
    }
    # cats to sum
    for cat in ['Value', 'PuntV', 'LeagV', 'pV', '3V', 'rV', 'aV', 'sV', 'bV', 'fg%V', 'ft%V', 'toV']:
        if cat in stats_df.columns:
            new_row[cat] = round(stats_df.loc[:, cat].astype(float).sum(), 2)

    for cat in ['m/g', 'p/g', '3/g', 'r/g', 'a/g', 's/g', 'b/g', 'to/g']:
        new_row[cat] = round(stats_df.loc[:, cat].astype(float).mean(), 2)

    final_df = stats_df.append(new_row, ignore_index=True)
    return final_df

