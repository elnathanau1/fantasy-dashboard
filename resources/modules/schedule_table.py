from resources.services.schedule_service import *
from dash import dash_table
import pandas as pd
from resources.util import get_color


def generate_schedule_table(week):
    league_obj = get_league_obj()
    row_list = []
    for team in league_obj.teams:
        row = {
            'Team': team.team_name,
            'Total Est. Games': get_estimated_total_games(team.team_id, week, exclude_out=False, exclude_dtd=False),
            'Total Est. Games w/ Injuries': get_estimated_total_games(team.team_id, week)
        }
        if week == league_obj.currentMatchupPeriod:
            row['Est. Remaining Games'] = get_current_week_remaining_games(team.team_id, exclude_out=False, exclude_dtd=False)
        row_list.append(row)

    df = pd.DataFrame.from_dict(row_list)
    color_columns = list(df.columns)
    color_columns.remove('Team')

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
            , color_columns
        ))
        for new_style in new_styles:
            style.append(new_style)

    return dash_table.DataTable(
            data=df.to_dict('records'),
            sort_action='native',
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_data_conditional=style,
            style_cell={'textAlign': 'center'}
    )
