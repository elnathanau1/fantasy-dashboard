import pandas as pd
from dash import dash_table
from resources.services.espn_fantasy_service import get_player_info, get_player_headshot, get_team


def generate_trade_block_chart(trade_block):
    # list to turn into dataframe later
    trade_block_table = []
    for trade in trade_block:
        team = get_team(int(trade['team_id']))
        player_id = trade['player_id']
        # make sure only players on current rosters are on trade block
        if str(player_id) in list(map(lambda player: str(player.playerId), team.roster)):
            new_row = {
                'Team': trade['team_name'],
                'Player': '![]({0}){1}'.format(get_player_headshot(player_id), get_player_info(player_id)['fullName'])
            }
            trade_block_table.append(new_row)

    # turn into pandas dataframe
    trade_block_df = pd.DataFrame(trade_block_table)

    return dash_table.DataTable(
        data=trade_block_df.to_dict('records'),
        sort_action='native',
        columns=[
            dict(name='Team', id='Team', type='text'),
            dict(name='Player', id='Player', type='text', presentation='markdown')
        ],
        style_as_list_view=True,
        style_cell={'textAlign': 'center'}
    )
