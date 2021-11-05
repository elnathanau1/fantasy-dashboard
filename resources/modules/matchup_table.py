import pandas as pd
from dash import dash_table
from main_dash import app
from dash.dependencies import Input, Output, State
from resources.constants import *
from resources.services.espn_fantasy_service import get_week_matchup_stats
from resources.util import get_colors_stat_tables

DISPLAY_COLUMNS = ['Team', 'FG%', 'FT%', '3PTM', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS']


def generate_matchup_table(power_rankings):
    # list to turn into dataframe later
    matchup_table = []
    styles = []
    tooltips = []
    for team in power_rankings:
        new_row = {'Home Team': team['team']}
        new_tooltip = {}
        for matchup in team['matchups']:
            # NOTE: Swapping win/loss and colors to make the chart easier to read (hacky... TODO: make less hacky)
            result_string = "{0}-{1}-{2}".format(matchup['losses'], matchup['wins'], matchup['ties'])
            new_row[matchup['away_team']] = result_string

            # determine cell color
            if matchup['wins'] > matchup['losses']:
                color = RED
            elif matchup['wins'] < matchup['losses']:
                color = GREEN
            else:
                color = GRAY
            # append the custom color to styles for the specific result string
            styles.append({
                'if': {
                    'filter_query': '{{{col}}} = {value}'.format(
                        col=matchup['away_team'], value=result_string
                    ),
                    'column_id': matchup['away_team'],
                },
                'backgroundColor': color,
                'color': 'white'
            })

            tooltip_value = '{0}: {1}\n\n{2}: {3}\n\n'.format(
                matchup['away_team'],
                ', '.join(matchup['lose_cats']),
                team['team'],
                ', '.join(matchup['win_cats'])
            )
            if matchup['ties'] != 0:
                tooltip_value += '\n\nTies: {0}'.format(', '.join(matchup['tie_cats']))

            new_tooltip[matchup['away_team']] = {
                'value': tooltip_value,
                'type': 'markdown'
            }

        tooltips.append(new_tooltip)
        matchup_table.append(new_row)

    # turn into pandas dataframe
    matchup_col_order = ['Home Team'] + list(map(lambda row: row['Home Team'], matchup_table))
    matchup_df = pd.DataFrame(matchup_table)[matchup_col_order]

    return dash_table.DataTable(
        id=MATCHUP_CHART,
        data=matchup_df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in matchup_df.columns],
        style_data_conditional=styles,
        style_as_list_view=True,
        style_cell={'textAlign': 'center'},
        tooltip_data=tooltips,
        tooltip_delay=0,
        tooltip_duration=None
    )


@app.callback(
    Output(TEAM_WEEK_COMPARISON_TABLE, 'children'),
    Input(MATCHUP_CHART, 'active_cell'),
    State(MATCHUP_CHART, 'data'),
    Input(WEEK_DROPDOWN_ID, 'value')
)
def generate_team_comparison_table(active_cell, data, week_id):
    if active_cell:
        week_matchup_stats = get_week_matchup_stats(int(week_id))

        away_team = active_cell['column_id']
        row = active_cell['row']
        home_team = data[row]['Home Team']

        list = [
            next(team for team in week_matchup_stats if team['team'] == away_team)['stats'],
            next(team for team in week_matchup_stats if team['team'] == home_team)['stats']
        ]
        list[0]['Team'] = away_team
        list[1]['Team'] = home_team

        df = pd.DataFrame(list)[DISPLAY_COLUMNS]

        return dash_table.DataTable(
            data=df.to_dict('records'),
            sort_action='native',
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_data_conditional=get_colors_stat_tables(df),
            style_cell={'textAlign': 'center'},
        )
    return None
