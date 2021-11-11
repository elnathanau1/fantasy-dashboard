from main_dash import app
from resources.services.espn_fantasy_service import get_today_streams
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, ALL
import json

STREAM_CONTAINER = 'stream_container'
STREAM_DROPDOWN_ID = 'stream_dropdown_id'
STREAM_IFRAME_CONTAINER = 'stream_iframe_container'
STREAM_ORIGIN_BUTTON = 'stream_origin_button'
GAME_SELECTION_CONTAINER_ID = 'game_selection_container_id'
STREAMS_PAGE_ID = 'streams_page_id'
STREAM_SOURCE_BUTTON_CONTAINER = 'stream_source_button_container'


def generate_streams_page():
    return html.Div(id=STREAMS_PAGE_ID, children=[
        dcc.Loading(
            id="loading-1",
            type="default",
            fullscreen=True,
            children=html.Div(id=GAME_SELECTION_CONTAINER_ID)
        ),
        dcc.Loading(
            id="loading-1",
            type="default",
            fullscreen=True,
            children=html.Div(id=STREAM_CONTAINER, style={'align': 'center'})
        )
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
        html.H2(today_streams[int(stream_index)]['name']),
        html.Iframe(
            id=STREAM_IFRAME_CONTAINER,
            src=today_streams[int(stream_index)]['streams'][0]['stream_url'],
            allow='fullscreen',
            sandbox="allow-forms allow-scripts allow-same-origin allow-top-navigation",
            style={
                'height': '75vh',
                'width': '75vw',
                'border': 'none'
            }
        ),
        html.P('Sources:'),
        html.Div(id=STREAM_SOURCE_BUTTON_CONTAINER, children=button_list),
        html.P("If this stream is not loading, load this page using http instead of https."),
        html.P("Working on a way to stream through a secure connection.")
    ]


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

