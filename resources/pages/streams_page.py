from main_dash import app
from resources.services.espn_fantasy_service import get_today_streams, get_player_info, get_player_headshot
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, ALL, State
import json
from resources.services.stream_service import get_live_games
from resources.page_css import streams_css as css
import time
from collections import deque

STREAM_CONTAINER = 'stream_container'
STREAM_DROPDOWN_ID = 'stream_dropdown_id'
STREAM_IFRAME_CONTAINER = 'stream_iframe_container'
STREAM_ORIGIN_BUTTON = 'stream_origin_button'
GAME_SELECTION_CONTAINER_ID = 'game_selection_container_id'
STREAMS_PAGE_ID = 'streams_page_id'
STREAM_SOURCE_BUTTON_CONTAINER = 'stream_source_button_container'
STORE_GAME_INFO = 'store_game_info'
PULL_GAME_INFO_INTERVAL = 'pull_game_info_interval'

STREAM_DELAY = 75  # seconds
PULL_INTERVAL_SECONDS = 2
MAX_STORE_SIZE = int(STREAM_DELAY / PULL_INTERVAL_SECONDS) + 50


def generate_streams_page():
    return html.Div(id=STREAMS_PAGE_ID, children=[
        dcc.Store(id=STORE_GAME_INFO, data=[]),
        dcc.Loading(
            id="loading-1",
            type="default",
            fullscreen=True,
            children=html.Div(id=GAME_SELECTION_CONTAINER_ID)
        ),
        html.Div(id=STREAM_CONTAINER, style={'align': 'center'})
    ])


@app.callback(Output(STREAM_CONTAINER, 'children'),
              Input(STREAM_DROPDOWN_ID, 'value'))
def render_team_page_container(stream_index):
    today_streams = get_today_streams()
    stream_list = today_streams[int(stream_index)]['streams']
    button_list = []
    for i in range(0, len(stream_list)):
        button_list.append(html.Button(
            stream_list[i]['name'],
            id={'type': 'source_button', 'index': i},
            type='source_button',
            value=stream_list[i]['stream_url']
        ))

    return [
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H2(today_streams[int(stream_index)]['name']),
                        html.Iframe(
                            id=STREAM_IFRAME_CONTAINER,
                            src=today_streams[int(stream_index)]['streams'][0]['stream_url'],
                            allow='fullscreen',
                            sandbox="allow-forms allow-scripts allow-same-origin allow-top-navigation",
                            style=css.STREAM_IFRAME_STYLE
                        ),
                        html.P('Sources:'),
                        html.Div(
                            id=STREAM_SOURCE_BUTTON_CONTAINER,
                            children=[
                                html.Div(children=button_list),
                                html.P(
                                    "If this stream is not loading, load this page using http instead of https."),
                                html.P("Working on a way to stream through a secure connection.")
                            ]
                        )
                    ]
                ),
                html.Div(id='live-update-text', style=css.STREAM_RECENT_PLAYS_STYLE)
            ],
            style=css.STREAM_GRID_STYLE
        ),
        dcc.Interval(
            id=PULL_GAME_INFO_INTERVAL,
            interval=PULL_INTERVAL_SECONDS * 1000,  # in milliseconds
            n_intervals=0
        )
    ]


@app.callback([Output('live-update-text', 'children'), Output(STORE_GAME_INFO, 'data')],
              Input(PULL_GAME_INFO_INTERVAL, 'n_intervals'),
              Input(STREAM_DROPDOWN_ID, 'value'),
              State(STORE_GAME_INFO, 'data'))
def update_metrics(n, stream_index, data):
    if data is None:
        return html.P("Waiting for stream to catch up to API"), list(q)
    else:
        q = deque(data, MAX_STORE_SIZE)
    live_games = get_live_games()
    timestamp = time.time()
    q.append({
        'games': live_games,
        'timestamp': timestamp
    })

    found = None
    while len(q) > 0 and timestamp - STREAM_DELAY > q[0]['timestamp']:
        if len(q) > 1 and timestamp - STREAM_DELAY > q[1]['timestamp']:
            found = q.popleft()['games']
        else:
            found = q[0]['games']
            break

    if found is None:
        return html.P("Waiting for stream to catch up to API"), list(q)

    live_games = found
    target_game = live_games[int(stream_index)]
    return_list = [
        html.H2("Active Players:")
    ]
    for i in range(0, 2):
        return_list.append(html.H3(target_game['teams'][i]))
        lineup_div_children = []
        for player in target_game['active_lineup'][i]:
            lineup_div_children.append(
                dcc.Markdown(
                    # f'![]({get_player_headshot(player["id"])}){get_player_info(player["id"])["fullName"]} - {player["position"]}',
                    f'{get_player_info(player["id"])["fullName"]} - {player["position"]} - {player["stats"]["PTS"]} PTS, ' +
                    f' {player["stats"]["3PM"]} 3PM, {player["stats"]["REB"]} REB, ' +
                    f'{player["stats"]["AST"]} AST, {player["stats"]["STL"]} STL, {player["stats"]["BLK"]} BLK'
                    # style=css.PLAYER_BOX_STYLE
                )
            )
        return_list.append(
            html.Div(children=lineup_div_children)
        )
    return_list.append(html.H2("Play by Play:"))
    return_list = return_list + list(map(
        lambda play: html.P(
            f"{clock_to_str(play['period'], play['clock'])} - {play['text']}",
            style=css.RECENT_PLAY_BOX_STYLE
        ),
        target_game['recent_plays']
    ))

    return html.Div(
        children=return_list
    ), list(q)


def clock_to_str(period, clock):
    quarter = f'Q{period}' if period <= 4 else f'{period - 4}OT'
    _, remainder = divmod(clock, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{} {:02}:{:02}'.format(quarter, int(minutes), int(seconds))


@app.callback(Output(STREAM_IFRAME_CONTAINER, 'src'),
              Input({'type': 'source_button', 'index': ALL}, 'n_clicks'),
              Input({'type': 'source_button', 'index': ALL}, 'value'),
              prevent_initial_call=True)
def render_team_page_container(clicks, values):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    changed_id_json = json.loads(changed_id.replace('.n_clicks', ''))
    index = changed_id_json['index']
    return values[index]


def dropdown_streams_list():
    today_streams = get_today_streams()
    return_list = []
    for i in range(0, len(today_streams)):
        return_list.append({
            'label': today_streams[i]['name'],
            'value': i
        })
    return return_list


@app.callback(Output(GAME_SELECTION_CONTAINER_ID, 'children'),
              Input(STREAMS_PAGE_ID, 'value'))
def generate_game_selector(value):
    return dcc.Dropdown(
        id=STREAM_DROPDOWN_ID,
        options=dropdown_streams_list(),
        value='0'
    )
