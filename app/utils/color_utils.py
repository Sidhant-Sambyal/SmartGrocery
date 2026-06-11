from math import pow


def shade_to_hex(shade: float) -> str:
    """
    Convert shade (0.0 - 1.0) into a blue color.

    0.0 -> light blue
    1.0 -> dark blue
    """

    shade = max(0.0, min(shade, 1.0))

    start = (173, 216, 230)
    end = (0, 51, 102)

    r = int(start[0] + (end[0] - start[0]) * shade)
    g = int(start[1] + (end[1] - start[1]) * shade)
    b = int(start[2] + (end[2] - start[2]) * shade)

    return f"#{r:02X}{g:02X}{b:02X}"


def get_text_color_for_bg(bg_hex: str) -> str:
    """
    Return #000000 or #FFFFFF — whichever gives a higher
    contrast ratio against *bg_hex*.

    Uses real WCAG 2.x relative-luminance math so we never
    pick the wrong side of the crossover point.
    """

    ratio_black = contrast_ratio(bg_hex, "#000000")
    ratio_white = contrast_ratio(bg_hex, "#FFFFFF")

    return "#000000" if ratio_black >= ratio_white else "#FFFFFF"


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")

    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def relative_luminance(hex_color: str):
    rgb = hex_to_rgb(hex_color)

    channels = []

    for value in rgb:
        value /= 255

        if value <= 0.03928:
            channels.append(value / 12.92)
        else:
            channels.append(pow((value + 0.055) / 1.055, 2.4))

    r, g, b = channels

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(background: str, foreground: str):

    l1 = relative_luminance(background)
    l2 = relative_luminance(foreground)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return round((lighter + 0.05) / (darker + 0.05), 2)