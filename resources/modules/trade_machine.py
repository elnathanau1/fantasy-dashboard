from resources.services.espn_fantasy_service import *
from dash import html, dcc
from resources.util import dropdown_teams_list, get_color, append_agg_stats_to_stats_table
from main_dash import app
from dash.dependencies import Input, Output
from dash import dash_table

TRADE_MACHINE_TEAM_1_DROPDOWN_ID = 'trade_machine_team_1_dropdown_id'
TRADE_MACHINE_TEAM_1_PLAYERS_CONTAINER_ID = 'trade_machine_team_1_players_container_id'
TRADE_MACHINE_TEAM_1_PLAYERS_DROPDOWN_ID = 'trade_machine_team_1_players_dropdown_id'
TRADE_MACHINE_TEAM_1_STATS_CONTAINER_ID = 'trade_machine_team_1_stats_container_id'

TRADE_MACHINE_TEAM_2_DROPDOWN_ID = 'trade_machine_team_2_dropdown_id'
TRADE_MACHINE_TEAM_2_PLAYERS_CONTAINER_ID = 'trade_machine_team_2_players_container_id'
TRADE_MACHINE_TEAM_2_PLAYERS_DROPDOWN_ID = 'trade_machine_team_2_players_dropdown_id'
TRADE_MACHINE_TEAM_2_STATS_CONTAINER_ID = 'trade_machine_team_2_stats_container_id'

TRADE_MACHINE_COMPARISON_CONTAINER_ID = 'trade_machine_comparison_container_id'


def generate_trade_machine():
    return html.Div([
        html.Div([
            html.P("Team A:"),
            dcc.Dropdown(
                id=TRADE_MACHINE_TEAM_1_DROPDOWN_ID,
                options=dropdown_teams_list(),
                value='1'
            ),
            html.Div(id=TRADE_MACHINE_TEAM_1_PLAYERS_CONTAINER_ID)
        ]),
        html.Div([
            html.P("Team B:"),
            dcc.Dropdown(
                id=TRADE_MACHINE_TEAM_2_DROPDOWN_ID,
                options=dropdown_teams_list(),
                value='1'
            ),
            html.Div(id=TRADE_MACHINE_TEAM_2_PLAYERS_CONTAINER_ID)
        ]),
        html.Div([
            html.P("Team A Gives:"),
            html.Div(id=TRADE_MACHINE_TEAM_1_STATS_CONTAINER_ID),
            html.P("Team B Gives:"),
            html.Div(id=TRADE_MACHINE_TEAM_2_STATS_CONTAINER_ID),
            html.Div(id=TRADE_MACHINE_COMPARISON_CONTAINER_ID)
        ])
    ])


@app.callback(Output(TRADE_MACHINE_TEAM_1_PLAYERS_CONTAINER_ID, 'children'),
              Input(TRADE_MACHINE_TEAM_1_DROPDOWN_ID, 'value'))
def render_player_dropdown(team_id):
    return render_player_dropdown_helper(team_id, TRADE_MACHINE_TEAM_1_PLAYERS_DROPDOWN_ID)


@app.callback(Output(TRADE_MACHINE_TEAM_2_PLAYERS_CONTAINER_ID, 'children'),
              Input(TRADE_MACHINE_TEAM_2_DROPDOWN_ID, 'value'))
def render_player_dropdown(team_id):
    return render_player_dropdown_helper(team_id, TRADE_MACHINE_TEAM_2_PLAYERS_DROPDOWN_ID)


def render_player_dropdown_helper(team_id, dropdown_id):
    team = get_team(int(team_id))
    roster = team.roster
    options = list(map(lambda player: {
        'label': player.name,
        'value': player.playerId
    }, roster))

    return dcc.Dropdown(
        id=dropdown_id,
        options=options,
        multi=True
    )


@app.callback(Output(TRADE_MACHINE_TEAM_1_STATS_CONTAINER_ID, 'children'),
              [Input(component_id=TRADE_MACHINE_TEAM_1_PLAYERS_DROPDOWN_ID, component_property='value')])
def render_player_stats(player_ids):
    if player_ids is None:
        return None
    return render_player_stats_helper(player_ids)


@app.callback(Output(TRADE_MACHINE_TEAM_2_STATS_CONTAINER_ID, 'children'),
              [Input(component_id=TRADE_MACHINE_TEAM_2_PLAYERS_DROPDOWN_ID, component_property='value')])
def render_player_stats(player_ids):
    if player_ids is None:
        return None
    return render_player_stats_helper(player_ids)


def render_player_stats_helper(player_ids):
    player_stats = get_player_stats()
    filtered_players = player_stats[player_stats['espn_id'].isin(player_ids)]
    filtered_players = append_agg_stats_to_stats_table(filtered_players)

    columns = list(filtered_players.columns)
    columns.remove('espn_id')
    columns.remove('Fantasy Team')

    style = []
    for index, row in filtered_players.iterrows():
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
        data=filtered_players.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in columns],
        style_data_conditional=style
    )


@app.callback(Output(TRADE_MACHINE_COMPARISON_CONTAINER_ID, 'children'),
              [Input(TRADE_MACHINE_TEAM_1_PLAYERS_DROPDOWN_ID, 'value'),
              Input(TRADE_MACHINE_TEAM_2_PLAYERS_DROPDOWN_ID, 'value')])
def render_player_stats(t1_player_ids, t2_player_ids):
    if t1_player_ids is not None and t2_player_ids is not None:
        player_stats = get_player_stats()
        team_1_stats = append_agg_stats_to_stats_table(player_stats[player_stats['espn_id'].isin(t1_player_ids)])
        team_2_stats = append_agg_stats_to_stats_table(player_stats[player_stats['espn_id'].isin(t2_player_ids)])

        print(team_1_stats[team_1_stats['Name'] == 'Avg/Total Values'].iloc[0].subtract(team_2_stats[team_2_stats['Name'] == 'Avg/Total Values'].iloc[0], numeric_only = True))


