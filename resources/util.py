from colour import Color


def get_color(val, max_val, min_val):
    val = float(val)
    avg = max_val / 2.0 + min_val / 2.0
    if max_val == avg:
        return Color(rgb=(1, 1, 1)).get_hex_l()

    score = abs((max_val - avg) - abs(val - avg)) / (max_val - avg)
    if score > 1.0:
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
