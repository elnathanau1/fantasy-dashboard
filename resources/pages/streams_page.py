from main_dash import app
from resources.services.espn_fantasy_service import get_today_game_streams
from dash import html, dcc
from dash.dependencies import Input, Output

STREAM_CONTAINER = 'stream_container'
STREAM_DROPDOWN_ID = 'stream_dropdown_id'


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
    today_streams = get_today_game_streams()

    return [
        html.H2(today_streams[int(stream_index)]['name']),
        html.Iframe(
            src=today_streams[int(stream_index)]['stream_url'],
            allow='fullscreen',
            style={
                'height': '75vh',
                'width': '75vw'
            }
        )
    ]


def dropdown_streams_list():
    today_streams = get_today_game_streams()
    return_list = []
    for i in range(0, len(today_streams)):
        return_list.append({
            'label': today_streams[i]['name'],
            'value': i
        })
    return return_list
