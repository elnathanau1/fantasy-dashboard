from colour import Color


def get_color(val, max_val, min_val):
    val = float(val)
    avg = max_val / 2.0 + min_val / 2.0

    score = abs((max_val - avg) - abs(val - avg))/(max_val - avg)
    if score > 1.0:
        score = 1.0

    if val > avg:
        return Color(rgb=(score, 1, score)).get_hex_l()
    else:
        return Color(rgb=(1, score, score)).get_hex_l()
