import pandas as pd
from dash import dash_table
from resources.constants import GREEN, RED, GRAY


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
