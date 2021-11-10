from main_dash import app
from resources.services.espn_fantasy_service import get_today_streams
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output

STREAM_CONTAINER = 'stream_container'
STREAM_DROPDOWN_ID = 'stream_dropdown_id'
STREAM_IFRAME_CONTAINER = 'stream_iframe_container'
STREAM_ORIGIN_BUTTON = 'stream_origin_button'


def generate_streams_page():
    return html.Div([
        dcc.Dropdown(
            id=STREAM_DROPDOWN_ID,
            options=dropdown_streams_list(),
            value='0'
        ),
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id=STREAM_CONTAINER)
        )
    ])


@app.callback(Output(STREAM_CONTAINER, 'children'),
              Input(STREAM_DROPDOWN_ID, 'value'))
def render_team_page_container(stream_index):
    today_streams = get_today_streams()
    # button_list = list(map(
    #     lambda stream: html.Button(
    #         stream['src'],
    #         id=f'{stream["src"]}_BUTTON',
    #         value=stream['stream_url']
    #     ),
    #     today_streams[int(stream_index)]['streams']
    # ))

    return [
        html.H2(today_streams[int(stream_index)]['name']),
        html.Iframe(
            id=STREAM_IFRAME_CONTAINER,
            src=today_streams[int(stream_index)]['streams'][0]['stream_url'],
            allow='fullscreen',
            style={
                'height': '75vh',
                'width': '75vw'
            }
        ),
        # html.Div(button_list),
        html.P("If this stream is not loading, load this page using http instead of https."),
        html.P("Working on a way to stream through a secure connection.")
    ]


# @app.callback(Output(STREAM_IFRAME_CONTAINER, 'src'),
#               Input('WEAKSTREAMS_BUTTON', 'n_clicks'),
#               Input('WEAKSTREAMS_BUTTON', 'value'),
#               # Input('TECHOREELS - (ADS)_BUTTON', 'n_clicks'),
#               # Input('TECHOREELS - (ADS)_BUTTON', 'value'),
#               Input(STREAM_IFRAME_CONTAINER, 'src'))
# def render_team_page_container(weakstream_click, weakstream_url, techoreels_click, techoreels_url, default_url):
#     changed_id = [p['prop_id'] for p in callback_context.triggered][0]
#     if 'WEAKSTREAMS_BUTTON' in changed_id:
#         return weakstream_url
#     elif 'TECHOREELS - (ADS)_BUTTON' in changed_id:
#         return techoreels_url
#     else:
#         return default_url


def dropdown_streams_list():
    today_streams = get_today_streams()
    return_list = []
    for i in range(0, len(today_streams)):
        return_list.append({
            'label': today_streams[i]['name'],
            'value': i
        })
    return return_list


